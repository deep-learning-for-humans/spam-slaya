from flask import Flask, current_app, redirect, request, session, url_for, render_template

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from utils import *

import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
app.secret_key = "foobar"  # Replace with a real secret key
with app.app_context():
    current_app.config["OPENAI_API_KEY"] = None

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.readonly",
]

# Replace with your OAuth 2.0 client ID file path
CLIENT_SECRETS_FILE = "client_secret.json"


@app.route("/")
def index():
    return render_template("index.html")
    # return '<a href="/login">Login with Gmail</a>'


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
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    return redirect(url_for("llm_activate"))


@app.route("/llm-activate")
def llm_activate():
    with app.app_context():
        if not current_app.config["OPENAI_API_KEY"]:
            return render_template("llm_activate.html")
        else:
            return redirect(url_for("gmail_actions"))


@app.route("/store-key", methods=["POST"])
def handle_form_submission():
    # Get the API key from the form data
    api_key = request.form.get("api_key")
    with app.app_context():
        current_app.config["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key

    print(os.environ["OPENAI_API_KEY"])

    return redirect(url_for("gmail_actions"))


@app.route("/gmail_actions")
def gmail_actions():
    if "credentials" not in session:
        return redirect("login")

    credentials = Credentials(**session["credentials"])
    service = build("gmail", "v1", credentials=credentials)

    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    email_list = []
    for message in messages:

        msg_raw = service.users().messages().get(userId="me", id=message["id"], format="raw").execute()

        body = get_email_body(msg_raw["raw"])
        subject = get_email_subject(msg_raw["raw"])

        del_action = infer_email_type(body)

        email_list.append(
            {
                "id": message["id"],
                "subj": subject,
                "body": body,
                "to_delete": del_action,
            }
        )

    return "OK"


if __name__ == "__main__":
    app.run("localhost", 8080, debug=True)
