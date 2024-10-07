from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    print(f"db url: {Config.SQLALCHEMY_DATABASE_URI}")
    print(f"client secrets path: {Config.CLIENT_SECRET_PATH}")

    # Initialize extensions
    db.init_app(app)

    from .models import User, Run, RunBatch

    with app.app_context():
        print(f"Calling create_all on DB: [{Config.SQLALCHEMY_DATABASE_URI}]")
        db.create_all()

    # Register routes
    from . import views
    views.register_routes(app)

    return app
