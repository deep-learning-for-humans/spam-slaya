import datetime
import json

import redis
from rq import Queue

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import db
from . import create_app
from .models import User, Run, RunBatch, RunStatusEnum
from .config import Config
from .utils import email, ai

redis_conn = redis.from_url(Config.RQ_BROKER_URL)
q = Queue(connection=redis_conn)

def schedule_bg_run(user_id):
    print(f"scheduling run for {user_id}")

    user = User.query.get(user_id)
    if not user:
        print(f"Couldn't find user {user_id}. Exiting")
        return

    if not user.gmail_credentials:
        print(f"Gmail credentials not found for {user_id}. Exiting")
        return
    elif datetime.datetime.utcnow() > user.gmail_credential_expiry:
        print(f"Gmail credentials are expired for {user_id}. Exiting")
        return

    if not user.open_api_key:
        print(f"Open API key not found for {user_id}. Exiting")
        return

    new_run = Run(
        user_id = user_id
    )

    db.session.add(new_run)
    db.session.commit()

    print(f"All OK. Proceeding to run the job in the background for user {user_id}")

    q.enqueue(bg_process_run, new_run.id)

    return new_run

def bg_process_run(run_id):

    print(f"Running job {run_id} in backgroun")

    app = create_app()
    with app.app_context():
        run = Run.query.get(run_id)
        if not run:
            print(f"FATAL. Unable to find run {run_id}. Exiting")
            return

        run.started_at = datetime.datetime.utcnow()
        run.status = RunStatusEnum.PROCESSING

        db.session.add(run)
        db.session.commit()

        print(f"Marked job as processing")

        user = User.query.get(run.user_id)

        credentials = Credentials.from_authorized_user_info(json.loads(user.gmail_credentials))
        service = build("gmail", "v1", credentials=credentials)

        results = service.users().messages().list(userId="me", maxResults=5).execute()
        messages = results.get("messages", [])

        print(f"Got {len(messages)} messages to process")

        message_count = len(messages)
        i=0
        for message in messages:

            i+=1
            print(f"Processing message {i} of {message_count}")

            msg_raw = service.users().messages().get(userId="me", id=message["id"], format="raw").execute()

            body = email.get_email_body(msg_raw["raw"])
            subject = email.get_email_subject(msg_raw["raw"])

            del_action = ai.infer_email_type(user.open_api_key, body)

            print(f"Message {subject} Action: {del_action}")

        run.ended_at = datetime.datetime.utcnow()
        run.status = RunStatusEnum.DONE

        db.session.add(run)
        db.session.commit()
