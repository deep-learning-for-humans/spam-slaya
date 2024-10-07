from redis import Redis
from rq import Worker

from app.config import Config

listen = ['default']
redis_conn = Redis.from_url(Config.RQ_BROKER_URL)

if __name__ == "__main__":
    worker = Worker(listen, connection=redis_conn)
    worker.work(logging_level="DEBUG")
