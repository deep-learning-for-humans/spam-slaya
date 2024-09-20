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
from .utils import email as email_utils, ai as ai_utils

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

    print(f"Running job {run_id} in background")

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

        BATCH_SIZE = 2

        results = service.users().messages().list(userId="me", maxResults=BATCH_SIZE).execute()
        messages = results.get("messages", [])

        count = 1

        while len(messages) > 0:

            #todo remove this
            if count == 3:
                print("breaking")
                break

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

            process_batch(credentials, batch_id, user.open_api_key)

            page_token = results.get("nextPageToken", None)
            if page_token:
                results = service.users().messages().list(userId="me", maxResults=BATCH_SIZE, pageToken = page_token).execute()
                messages = results.get("messages", [])

            count += 1

        batch_has_errors = RunBatch.query.filter(
            RunBatch.run_id == run.id,
            RunBatch.action == MessageActionEnum.UNPROCESSED
        ).count() > 0

        run.ended_at = datetime.datetime.utcnow()
        run.status = RunStatusEnum.DONE_WITH_ERRORS if batch_has_errors else RunStatusEnum.DONE

        db.session.add(run)
        db.session.commit()


def process_batch(credentials, batch_id, open_api_key):

        service = build("gmail", "v1", credentials=credentials)

        messages = RunBatch.query.filter_by(batch_id = batch_id)

        message_count = messages.count()
        for index, message in enumerate(messages, start=1):

            print(f"[{batch_id}] Processing message {index} of {message_count}")

            email = service.users().messages().get(userId="me", id=message.message_id, format="raw").execute()

            try:
                body = email_utils.get_email_body(email["raw"])
                subject = email_utils.get_email_subject(email["raw"])

                ai_inference = ai_utils.infer_email_type(open_api_key, body)

                print(f"Message {subject} Inference: {ai_inference}")

                message.subject = subject
                message.action = MessageActionEnum[ai_inference.action]

            except Exception as ex:
                print(f"Exception: When processing message {message.message_id} with message {ex}")

                message.action = MessageActionEnum.UNPROCESSED
                message.errors = repr(ex)

            db.session.add(message)
            db.session.commit()

