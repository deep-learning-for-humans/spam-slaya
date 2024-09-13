from flask import request, jsonify, render_template, url_for, session, redirect

from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow

from . import db
from .models import User

#from .tasks.task_1 import long_running_task

import os, json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid"
]

# Replace with your OAuth 2.0 client ID file path
CLIENT_SECRETS_FILE = "client_secret.json"


def register_routes(app):
    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login():
        flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = url_for("oauth2callback", _external=True)
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )
        session["state"] = state
        return redirect(authorization_url)

    @app.route("/oauth2callback")
    def oauth2callback():
        state = session["state"]
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
        )
        flow.redirect_uri = url_for("oauth2callback", _external=True)

        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials

        credential_parts = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        id_token = credentials.id_token
        id_info = verify_oauth2_token(id_token, requests.Request())
        user_id = id_info.get('sub')

        session["user"] = user_id

        user = User.query.filter_by(id=user_id).first()

        if not user:
            new_user = User(
                id=user_id,
                gmail_credentials=json.dumps(credential_parts)
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("activate_llm"))
        else:
            session["user"] = user_id
            if not user.open_api_key:
                return redirect(url_for("activate_llm"))
            else:
                return "All ready"

    @app.route("/activate-llm", methods=["GET", "POST"])
    def activate_llm():

        user_id = session["user"]

        if not user_id:
            return redirect(url_for("login"))

        user = User.query.filter_by(id=user_id).first()

        if not user:
            return redirect(url_for("login"))

        if request.method == "GET":
            if not user.open_api_key:
                return render_template("activate-llm.html")
            else:
                return "OK"
        elif request.method == "POST":
            key = request.form["key"]

            user.open_api_key = key
            db.session.add(user)
            db.session.commit()
            return "OK. stored"
            # handle key empty with flash

    #@app.route('/users', methods=['POST'])
    #def create_user():
    #    data = request.json
    #    user = User(username=data['username'], email=data['email'])
    #    db.session.add(user)
    #    db.session.commit()
    #    return jsonify({'message': 'User created successfully'}), 201

    #@app.route('/run-task', methods=['POST'])
    #def run_task():
    #    data = request.json
    #    result = long_running_task.delay(data['x'], data['y'])
    #    return jsonify({'task_id': result.id}), 202

#@app.route("/store-key", methods=["POST"])
#def handle_form_submission():
#    # Get the API key from the form data
#    api_key = request.form.get("api_key")
#    with app.app_context():
#        current_app.config["OPENAI_API_KEY"] = api_key
#        os.environ["OPENAI_API_KEY"] = api_key
#
#    print(os.environ["OPENAI_API_KEY"])
#
#    return redirect(url_for("gmail_actions"))
#
#
#@app.route("/gmail_actions")
#def gmail_actions():
#    if "credentials" not in session:
#        return redirect("login")
#
#    credentials = Credentials(**session["credentials"])
#    service = build("gmail", "v1", credentials=credentials)
#
#    results = service.users().messages().list(userId="me", maxResults=5).execute()
#    messages = results.get("messages", [])
#
#    email_list = []
#    for message in messages:
#
#        msg_raw = service.users().messages().get(userId="me", id=message["id"], format="raw").execute()
#
#        body = get_email_body(msg_raw["raw"])
#        subject = get_email_subject(msg_raw["raw"])
#
#        del_action = infer_email_type(body)
#
#        email_list.append(
#            {
#                "id": message["id"],
#                "subj": subject,
#                "body": body,
#                "to_delete": del_action,
#            }
#        )
#
#    return "OK"
