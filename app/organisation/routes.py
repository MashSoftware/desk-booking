from datetime import datetime

import pytz
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.exceptions import Forbidden

from app import db, limiter
from app.models import Organisation
from app.organisation import bp
from app.organisation.forms import OrganisationDeleteForm, OrganisationForm


@bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def create():
    """Create a new Organisation."""

    # Prevent authenticated users from creating a new organisation if they're already in one
    if current_user.organisation_id:
        raise Forbidden()

    form = OrganisationForm()

    if form.validate_on_submit():
        new_organisation = Organisation(name=form.name.data.strip(), domain=form.domain.data.strip())
        current_user.organisation_id = new_organisation.id
        current_user.role = "admin"
        db.session.add(new_organisation)
        db.session.add(current_user)
        db.session.commit()
        flash(
            f"<a href='{url_for('organisation.view')}' class='alert-link'>{new_organisation.name}</a> has been created.",
            "success",
        )
        return redirect(url_for("main.index"))

    return render_template("create_organisation.html", title="Create a new organisation", form=form)


@bp.route("/", methods=["GET"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def view():
    """View the authenticated users organisation."""
    return render_template("view_organisation.html", title=current_user.organisation.name)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def edit():
    """Edit the authenticated users organisation."""

    # Only allow admins to edit their own organisation
    if current_user.role != "admin":
        raise Forbidden()

    form = OrganisationForm()

    if form.validate_on_submit():
        current_user.organisation.name = form.name.data.strip()
        current_user.organisation.domain = form.domain.data.lower().strip()
        current_user.organisation.updated_at = pytz.utc.localize(datetime.utcnow())
        db.session.add(current_user)
        db.session.commit()
        flash(
            f"Your changes to <a href='{url_for('organisation.view')}' class='alert-link'>{current_user.organisation.name}</a> have been saved.",
            "success",
        )
        return redirect(url_for("main.index"))
    elif request.method == "GET":
        form.name.data = current_user.organisation.name
        form.domain.data = current_user.organisation.domain

    return render_template(
        "update_organisation.html",
        title="Edit organisation",
        form=form,
    )


@bp.route("/delete", methods=["GET", "POST"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def delete():
    """Delete the authenticated users organisation."""

    # Only allow admins to delete their own organisation
    if current_user.role != "admin":
        raise Forbidden()

    form = OrganisationDeleteForm()

    if request.method == "GET":
        return render_template(
            "delete_organisation.html",
            title="Delete organisation",
            form=form,
        )
    elif request.method == "POST":
        org = current_user.organisation.name
        db.session.delete(current_user.organisation)
        db.session.commit()
        flash(f"{org} has been deleted.", "success")
        return redirect(url_for("main.index"))
