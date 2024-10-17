import os
from dotenv import load_dotenv

class Config:

    load_dotenv()

    dry_run_value = os.environ.get("SPAM_SLAYA_DRY_RUN")
    DRY_RUN = dry_run_value.upper() == "TRUE" if dry_run_value else False

    MAX_MESSAGES_PER_SCHEDULE = os.environ.get("SPAM_SLAYA_MAX_MESSAGES_PER_SCHEDULE") or 300

    LABEL = os.environ.get("SPAM_SLAYA_LABEL_NAME") or "SpamSlaya"

    SECRET_KEY = os.environ.get("SPAM_SLAYA_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get("SPAM_SLAYA_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RQ_BROKER_URL = os.environ.get("SPAM_SLAYA_RQ_BROKER_URL")

    CLIENT_SECRET_PATH = os.environ.get("SPAM_SLAYA_GOOGLE_CLIENT_SECRET_PATH")

    OLLAMA_URL = os.environ.get("SPAM_SLAYA_OLLAMA_URL") or "http://localhost:11434"
    OLLAMA_API_KEY = os.environ.get("SPAM_SLAYA_OLLAMA_API_KEY") or ""
    OLLAMA_MODEL = os.environ.get("SPAM_SLAYA_OLLAMA_MODEL") or "qwen2.5:3b-instruct-q4_0"
