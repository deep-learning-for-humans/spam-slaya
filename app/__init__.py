from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from .config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Celery
#celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

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

#def init_celery(celery, app):
#    celery.conf.update(app.config)
#    TaskBase = celery.Task
#
#    class ContextTask(TaskBase):
#        def __call__(self, *args, **kwargs):
#            with app.app_context():
#                return TaskBase.__call__(self, *args, **kwargs)
#
#    celery.Task = ContextTask
