import os

import redis
from rq import Worker, Queue, Connection

from app.config import Config

listen = ['default']
conn = redis.from_url(Config.RQ_BROKER_URL)

if __name__ == "__main__":
    worker = Worker(listen, connection=conn)
    worker.work()
