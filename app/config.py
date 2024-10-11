import os
from dotenv import load_dotenv

class Config:

    load_dotenv()

    SECRET_KEY = os.environ.get("SPAM_SLAYA_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get("SPAM_SLAYA_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RQ_BROKER_URL = os.environ.get("SPAM_SLAYA_RQ_BROKER_URL")

    CLIENT_SECRET_PATH = os.environ.get("SPAM_SLAYA_GOOGLE_CLIENT_SECRET_PATH")

    OLLAMA_URL = os.environ.get("SPAM_SLAYA_OLLAMA_URL")
    OLLAMA_MODEL = os.environ.get("SPAM_SLAYA_OLLAMA_MODEL")
