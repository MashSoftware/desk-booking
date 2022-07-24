import os


class Config(object):
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
        if os.environ.get("DATABASE_URL")
        else "postgresql://mash:mash@localhost:5432/mash"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 20}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TIMEOUT = int(os.environ.get("TIMEOUT"))
