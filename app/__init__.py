from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

from celery import Celery
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    from .models import User, Run, RunBatch

    with app.app_context():
        db.create_all()

    # Register routes
    from . import views
    views.register_routes(app)

    return app
