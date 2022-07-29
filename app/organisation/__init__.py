from flask import Blueprint

bp = Blueprint(
    "organisation",
    __name__,
    template_folder="../templates/organisation",
    url_prefix="/organisations",
)

from app.organisation import routes  # noqa: E402,F401
