import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import pickle
from flask import Flask, request, redirect, session, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = 'foobar'  # Replace with a real secret key

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.readonly']

# Replace with your OAuth 2.0 client ID file path
CLIENT_SECRETS_FILE = "client_secret.json"


@app.route('/')
def index():
    return '<a href="/login">Login with Gmail</a>'


@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(url_for('gmail_actions'))


@app.route('/gmail_actions')
def gmail_actions():
    if 'credentials' not in session:
        return redirect('login')

    credentials = Credentials(**session['credentials'])
    service = build('gmail', 'v1', credentials=credentials)

    # Here you can implement your Gmail actions (read, move, delete)
    # For example:
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    email_list = ""
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_list += f"Subject: {msg['payload']['headers'][0]['value']}<br>"
        email_list += f"Snippet: {msg['snippet']}<br><br>"

    return f"Here are your recent emails:<br><br>{email_list}"


if __name__ == '__main__':
    app.run('localhost', 8080, debug=True)