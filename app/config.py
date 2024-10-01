import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'foobar'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////Users/raghothams/code/clean-that-up/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RQ_BROKER_URL = os.environ.get('RQ_BROKER_URL') or 'redis://0.0.0.0:6379/0'
