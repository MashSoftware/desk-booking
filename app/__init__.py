import logging

from flask import Flask
from flask_assets import Bundle, Environment
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

from config import Config

assets = Environment()
compress = Compress()
csrf = CSRFProtect()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address, default_limits=["2 per second", "60 per minute"])
login = LoginManager()
login.login_message_category = "info"
login.login_view = "user.login"
login.needs_refresh_message = "To protect your account, please log in again to access this page."
login.needs_refresh_message_category = "info"
login.refresh_view = "user.login"
migrate = Migrate()
talisman = Talisman()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    # Set content security policy
    csp = {
        "default-src": "'self'",
        "style-src": ["https://cdn.jsdelivr.net", "'self'"],
        "script-src": ["https://cdn.jsdelivr.net", "'self'"],
        "font-src": "https://cdn.jsdelivr.net",
        "img-src": [
            "https://cdn.jsdelivr.net",
            "data:",
            "'self'",
        ],
    }

    # Initialise app extensions
    assets.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    talisman.init_app(app, content_security_policy=csp)

    # Create static asset bundles
    css = Bundle("src/css/*.css", filters="cssmin", output="dist/css/custom-%(version)s.min.css")
    js = Bundle("src/js/*.js", filters="jsmin", output="dist/js/custom-%(version)s.min.js")
    if "css" not in assets:
        assets.register("css", css)
    if "js" not in assets:
        assets.register("js", js)

    # Register blueprints
    from app.main import bp as main_bp
    from app.thing import bp as thing_bp
    from app.user import bp as user_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(thing_bp)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Startup")

    return app


from app import models  # noqa: E402,F401
