import datetime

import redis
from rq import Queue

from . import db
from .models import User, Run, RunBatch
from .config import Config

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