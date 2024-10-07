import uuid
import datetime
import json
import os

from flask import request, render_template, url_for, session, redirect, flash, abort

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

from ollama import Client as OllamaClient

from . import db
from .models import User, Run, RunBatch, RunStatusEnum, MessageActionEnum
from .config import Config
from .tasks import schedule_bg_run, bg_download_model


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid"
]

redis_conn = Redis.from_url(Config.RQ_BROKER_URL)
q = Queue(connection=redis_conn)

ollama = OllamaClient(host=Config.OLLAMA_URL)

def register_routes(app):
    @app.route('/')
    def index():
        list_response = ollama.list()
        models = list_response['models']
        has_required_model = any(model["name"] == Config.OLLAMA_MODEL for model in models)

        if not has_required_model:
            is_downloading = False
            try:
                job = Job.fetch("MODEL_DOWNLOAD", connection=redis_conn)
                status = job.get_status(refresh=True)

                if status == "started" or status == "queued" or status == "scheduled":
                    is_downloading = True
                else:
                    is_downloading = False
            except NoSuchJobError:
                pass

            if not is_downloading:
                q.enqueue(bg_download_model, job_timeout='1h', job_id="MODEL_DOWNLOAD")

        user_id = session.get("user")
        if user_id:
            return redirect(url_for("home"))

        return render_template("index.html", has_required_model=has_required_model)

    @app.route("/login")
    def login():
        flow = Flow.from_client_secrets_file(Config.CLIENT_SECRET_PATH, scopes=SCOPES)
        flow.redirect_uri = url_for("oauth2callback", _external=True)
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true",
            approval_prompt="force"
        )
        session["state"] = state
        return redirect(authorization_url)

    @app.route("/oauth2callback")
    def oauth2callback():
        state = session["state"]
        flow = Flow.from_client_secrets_file(
            Config.CLIENT_SECRET_PATH, scopes=SCOPES, state=state
        )
        flow.redirect_uri = url_for("oauth2callback", _external=True)

        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        id_token = credentials.id_token
        id_info = verify_oauth2_token(id_token, requests.Request(), clock_skew_in_seconds=5)
        user_id = id_info.get('sub')

        session["user"] = user_id

        user = User.query.filter_by(id=user_id).first()

        if not user:
            new_user = User(
                id=user_id,
                gmail_credentials=credentials.to_json(),
                gmail_credential_expiry=credentials.expiry
            )

            db.session.add(new_user)
            db.session.commit()
        else:
            expiry = user.gmail_credential_expiry
            if credentials.expiry > expiry:
                user.gmail_credentials = credentials.to_json()
                user.gmail_credential_expiry = credentials.expiry

                db.session.add(user)
                db.session.commit()

        return redirect(url_for("home"))

    @app.route("/home")
    def home():
        user_id = session.get("user")

        if not user_id:
            print("no user_id. Redirecting to login")
            return redirect(url_for("login"))

        user = User.query.filter_by(id=user_id).first()

        if not user or not user.gmail_credentials:
            # use flash here
            print("no user no gmail creds. Redirecting to login")
            return redirect(url_for("login"))

        print(datetime.datetime.utcnow(), user.gmail_credential_expiry)

        if datetime.datetime.utcnow() > user.gmail_credential_expiry:
            # credentials have expired. Flash this
            print("Credentials expired. Redirecting to login")
            return redirect(url_for("login"))

        credentials = Credentials.from_authorized_user_info(json.loads(user.gmail_credentials))
        service = build("gmail", "v1", credentials=credentials)

        user_profile = service.users().getProfile(userId = user_id).execute()
        total_messages = user_profile.get("messagesTotal", None)
        email_address = user_profile.get("emailAddress", None)

        runs = Run.query.filter_by(user_id = user_id).order_by(Run.scheduled_at.desc())
        runs_in_process = Run.query.filter(
            Run.user_id == user.id,
            Run.status != RunStatusEnum.DONE,
            Run.status != RunStatusEnum.DONE_WITH_ERRORS
        ).count() > 0

        return render_template("home.html",
                               runs=runs,
                               total_messages=total_messages,
                               runs_in_process=runs_in_process,
                               email_address=email_address)

    @app.route("/schedule-run", methods=["POST"])
    def schedule_run():
        user_id = session.get("user")

        if not user_id:
            print("no user_id. Redirecting to login")
            return redirect(url_for("login"))

        user = User.query.filter_by(id=user_id).first()

        if not user or not user.gmail_credentials:
            # use flash here
            print("no user or no gmail creds. Redirecting to login")
            return redirect(url_for("login"))

        if datetime.datetime.utcnow() > user.gmail_credential_expiry:
            # credentials have expired. Flash this
            print("Credentials expired. Redirecting to login")
            return redirect(url_for("login"))

        no_of_emails_to_process = request.form.get("no_of_emails_to_process", None)
        if not no_of_emails_to_process:
            flash("Missing required input - number of emails to process")
            return redirect(url_for("home"))

        runs_in_process = Run.query.filter(
            Run.user_id == user.id,
            Run.status != RunStatusEnum.DONE,
            Run.status != RunStatusEnum.DONE_WITH_ERRORS
        ).count() > 0

        if runs_in_process:
            flash("There is already a run in progress. Please wait for that to end to schedule another one")
            return redirect(url_for("home"))

        run = schedule_bg_run(user_id, no_of_emails_to_process)
        flash("Your run has been queued for processing")

        return redirect(url_for("run_status", run_id = run.id))

    @app.route("/run-status/<run_id>", methods=["GET"])
    def run_status(run_id):
        user_id = session.get("user")

        if not user_id:
            print("no user_id. Redirecting to login")
            return redirect(url_for("login"))

        user = User.query.filter_by(id=user_id).first()

        if not user or not user.gmail_credentials:
            # use flash here
            print("no user or no gmail creds. Redirecting to login")
            return redirect(url_for("login"))

        if datetime.datetime.utcnow() > user.gmail_credential_expiry:
            # credentials have expired. Flash this
            print("Credentials expired. Redirecting to login")
            return redirect(url_for("login"))

        run = Run.query.get(uuid.UUID(run_id))
        if not run:
            return abort(404)


        run_batches = RunBatch.query.filter_by(run_id = run.id)

        show = request.args.get("show", "ALL")
        if show == "KEEP":
            run_batches = run_batches.filter_by(action = MessageActionEnum.KEEP)
        elif show == "DELETE":
            run_batches = run_batches.filter_by(action = MessageActionEnum.DELETE)

        message_count = run_batches.count()

        message_process_count = RunBatch.query.filter(
            RunBatch.run_id == run.id,
            RunBatch.action != MessageActionEnum.TBD
            ).count()

        message_error_count = RunBatch.query.filter(
            RunBatch.run_id == run.id,
            RunBatch.action == MessageActionEnum.UNPROCESSED
            ).count()

        message_delete_count = RunBatch.query.filter(
            RunBatch.run_id == run.id,
            RunBatch.action == MessageActionEnum.DELETE
            ).count()

        return render_template("run_status.html", model = {
            "run": run,
            "count": message_count,
            "process_count": message_process_count,
            "error_count": message_error_count,
            "delete_count": message_delete_count,
            "batch_results": run_batches,
            "show_filter_value": show
        })
