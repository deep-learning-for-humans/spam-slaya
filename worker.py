
from redis import Redis
from rq import Worker

from app.config import Config

listen = ['default']
conn = Redis(host='redisserver', port=6379, db=0)

if __name__ == "__main__":
    worker = Worker(listen, connection=conn)
    worker.work(logging_level="DEBUG")
