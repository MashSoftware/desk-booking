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
            f"<a href='{url_for('organisation.view', id=new_organisation.id)}' class='alert-link'>{new_organisation.name}</a> has been created.",
            "success",
        )
        return redirect(url_for("main.index"))

    return render_template("create_organisation.html", title="Create a new organisation", form=form)


@bp.route("/<uuid:id>", methods=["GET"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def view(id):
    """Get a Organisation with a specific ID."""

    # Prevent authenticated users from viewing other organisations
    if current_user.organisation_id != str(id):
        raise Forbidden()

    organisation = Organisation.query.get_or_404(str(id))

    return render_template("view_organisation.html", title=organisation.name, organisation=organisation)


@bp.route("/<uuid:id>/edit", methods=["GET", "POST"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def edit(id):
    """Edit a Organisation with a specific ID."""

    # Prevent authenticated users from editing other organisations
    if current_user.organisation_id != str(id) or current_user.role != "admin":
        raise Forbidden()

    organisation = Organisation.query.get_or_404(str(id))
    form = OrganisationForm()

    if form.validate_on_submit():
        organisation.name = form.name.data.strip()
        organisation.domain = form.domain.data.lower().strip()
        organisation.updated_at = pytz.utc.localize(datetime.utcnow())
        db.session.add(organisation)
        db.session.commit()
        flash(
            f"Your changes to <a href='{url_for('organisation.view', id=organisation.id)}' class='alert-link'>{organisation.name}</a> have been saved.",
            "success",
        )
        return redirect(url_for("main.index"))
    elif request.method == "GET":
        form.name.data = organisation.name
        form.domain.data = organisation.domain

    return render_template(
        "update_organisation.html",
        title="Edit organisation",
        form=form,
        organisation=organisation,
    )


@bp.route("/<uuid:id>/delete", methods=["GET", "POST"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def delete(id):
    """Delete a Organisation with a specific ID."""

    # Prevent authenticated users from deleting other organisations
    if current_user.organisation_id != str(id) or current_user.role != "admin":
        raise Forbidden()

    organisation = Organisation.query.get_or_404(str(id))
    form = OrganisationDeleteForm()

    if request.method == "GET":
        return render_template(
            "delete_organisation.html",
            title="Delete organisation",
            form=form,
            organisation=organisation,
        )
    elif request.method == "POST":
        db.session.delete(organisation)
        db.session.commit()
        flash(f"{organisation.name} has been deleted.", "success")
        return redirect(url_for("main.index"))
