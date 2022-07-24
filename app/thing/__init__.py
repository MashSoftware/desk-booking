from flask import Blueprint

bp = Blueprint("thing", __name__, template_folder="../templates/thing", url_prefix="/things")

from app.thing import routes  # noqa: E402,F401
