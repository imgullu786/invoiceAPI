from datetime import timedelta
import os

from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

from .models import db, User, create_tables
load_dotenv()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # In production, load this from env variable
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "fallback-secret")
    app.config["REMEMBER_COOKIE_DURATION"] = os.getenv("COOKIE_DURATION")

    # --- Flask-Login setup ---
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.get_by_id(int(user_id))
        except User.DoesNotExist:
            return None

    # --- Peewee DB connection per request ---
    @app.before_request
    def _db_connect():
        if db.is_closed():
            db.connect()

    @app.teardown_request
    def _db_close(exc):
        if not db.is_closed():
            db.close()

    # --- Register blueprints ---
    from .auth import auth_bp
    from .routes import api_bp
    from .views import views_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    # --- Create tables if not exist ---
    with app.app_context():
        create_tables()

    return app
