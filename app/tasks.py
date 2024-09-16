import uuid
import datetime
import json

import redis
from rq import Queue

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import db
from . import create_app
from .models import User, Run, RunBatch, RunStatusEnum, MessageActionEnum
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

        results = service.users().messages().list(userId="me", maxResults=10).execute()
        messages = results.get("messages", [])

        print(f"Got {len(messages)} messages to process")

        batch_id = uuid.uuid4()
        for message in messages:
            batch = RunBatch(
                run_id = run_id,
                batch_id = batch_id,
                message_id = message["id"],
            )
            db.session.add(batch)

        db.session.commit()

        messages_to_process = RunBatch.query.filter_by(batch_id = batch_id)

        has_error = False
        message_count = messages_to_process.count()
        for index, message in enumerate(messages_to_process, start=1):

            print(f"Processing message {index} of {message_count}")

            msg_raw = service.users().messages().get(userId="me", id=message.message_id, format="raw").execute()

            try:
                body = email.get_email_body(msg_raw["raw"])
                subject = email.get_email_subject(msg_raw["raw"])

                ai_inference = ai.infer_email_type(user.open_api_key, body)

                print(f"Message {subject} Inference: {ai_inference}")

                message.action = MessageActionEnum[ai_inference.action]

            except Exception as ex:
                print(f"Exception: When processing message {message.message_id} with message {ex}")

                has_error = True
                message.action = MessageActionEnum.UNPROCESSED
                message.errors = repr(ex)

            db.session.add(message)
            db.session.commit()

        run.ended_at = datetime.datetime.utcnow()
        run.status = RunStatusEnum.DONE_WITH_ERRORS if has_error else RunStatusEnum.DONE

        db.session.add(run)
        db.session.commit()
