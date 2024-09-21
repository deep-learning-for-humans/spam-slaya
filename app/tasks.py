import traceback
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

"""
Does the due diligence and creates a Run object. Then enqueues a job to run in
the background (via RQ) with the run ID. 

Note: This can be done in the same bg_process_run function but because the
amount of credentials we have to check is quite high, thought it best to create
an abstraction here.
"""
def schedule_bg_run(user_id, no_of_emails_to_process):
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
        user_id = user_id,
        to_process = no_of_emails_to_process
    )

    db.session.add(new_run)
    db.session.commit()

    print(f"All OK. Proceeding to run the job in the background for user {user_id}")

    q.enqueue(bg_process_run, new_run.id)

    return new_run

"""
This is where the run begins processing. It will first set the relevant details
for audit (started at, status, etc) and then build the required objects from the
DB to call the Gmail APIs.

Then it gets a batch of emails from Gmail (the max here is 500). When it gets
this, it will add it to a RunBatch. A RunBatch is owned by a Run and is used to
split up processing. The idea is that if there are 1000 emails, then it can run
as 2 parallel jobs of 500 per batch. At this point however, because of rate
limit concerns, we are not choosing to run these are parallel jobs.

So once the $batch of emails is got from Gmail, it is added to a new RunBatch
and processed. This is done in the process_batch method. The idea is that in the
future, this process_batch can just be run in the background and with a few more
changes, the entire set of batches can run in parallel.

Once all the batches have finished processing, based on the error count, the Run
object is finalized with the required details
"""
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

        max_results = 500
        if run.to_process < 500:
            max_results = run.to_process
            no_of_batches = 1
        else:
            no_of_batches = run.to_process // max_results
            if run.to_process % max_results > 0:
                no_of_batches += 1

        print(f"To Process: [{run.to_process}]. Processing in [{no_of_batches}] batches with [{max_results}] in each batch")

        #####
        # FOR DEVELOPMENT
        # This must be removed before going live
        max_results = 2
        no_of_batches = 2
        #
        ######

        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])

        batch_count = 1
        while len(messages) > 0:

            if batch_count > no_of_batches:
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
                results = service.users().messages().list(userId="me", maxResults=max_results, pageToken = page_token).execute()
                messages = results.get("messages", [])

            batch_count += 1

        batch_has_errors = RunBatch.query.filter(
            RunBatch.run_id == run.id,
            RunBatch.action == MessageActionEnum.UNPROCESSED
        ).count() > 0

        run.ended_at = datetime.datetime.utcnow()
        run.status = RunStatusEnum.DONE_WITH_ERRORS if batch_has_errors else RunStatusEnum.DONE

        db.session.add(run)
        db.session.commit()


"""
This is where the email is actually processed with calls to Open AI. The batch
that is created in the bg_process_run method is processed here by taking emails
one by one from the batch. Because of the complexity in properly getting the
email body, we are getting the RAW email first and then using the stdlib email
module to extract the information that we need. This is then sent on to the AI
which decides if the email needs to be deleted or not. And if it needs to be, it
queues it up to be trashed. The trashing is done via a batch operation after
that particular RunBatch is completed.

As it processes each email, it writes the results to that row in the RunBatch. 
"""
def process_batch(credentials, batch_id, open_api_key):

        service = build("gmail", "v1", credentials=credentials)

        messages = RunBatch.query.filter_by(batch_id = batch_id)
        message_count = messages.count()
        msgs_to_delete = []

        for index, message in enumerate(messages, start=1):

            print(f"[{batch_id}] Processing message {index} of {message_count}")

            email = service.users().messages().get(userId="me", id=message.message_id, format="raw").execute()

            try:
                body = email_utils.get_email_body(email["raw"])
                subject = email_utils.get_email_subject(email["raw"])

                ai_inference = ai_utils.infer_email_type(open_api_key, body)

                print(f"Message {subject} Inference: {ai_inference}")

                message.subject = subject
                message.reason = ai_inference.reason
                message.action = MessageActionEnum[ai_inference.action]

                if ai_inference.action.upper() == "DELETE":
                    msgs_to_delete.append(message.message_id)

            except Exception as ex:
                print(f"Exception: When processing message {message.message_id} with message {ex}")
                print(traceback.format_exc())

                message.action = MessageActionEnum.UNPROCESSED
                message.errors = repr(ex)

            db.session.add(message)
            db.session.commit()

        print(f"Deleting messages: {msgs_to_delete}")
        if len(msgs_to_delete) > 0:
            try:
                body = {
                    "ids": msgs_to_delete,
                    "addLabelIds": ["TRASH"]
                }
                delete_resp = service.users().messages().batchModify(userId="me", body=body).execute()
                print("Batch delete success")
                print(delete_resp)

            except Exception as ex:
                print("Error while batch deleting")
                print(traceback.format_exc())




