import os
from dotenv import load_dotenv

class Config:

    load_dotenv()

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RQ_BROKER_URL = os.environ.get('RQ_BROKER_URL')

    CLIENT_SECRET_PATH = os.environ.get('GOOGLE_CLIENT_SECRET_PATH')

    OLLAMA_URL = os.environ.get("OLLAMA_URL")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL")
