from datetime import datetime

import pytz
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, fresh_login_required, login_required, login_user, logout_user
from werkzeug.exceptions import Forbidden
from werkzeug.urls import url_parse

from app import db, limiter
from app.models import Organisation, User
from app.user import bp
from app.user.forms import LoginForm, SignupForm, UserDeleteForm, UserForm


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("user.view", id=current_user.id))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email_address=form.email_address.data,
            password=form.password.data,
            timezone=form.timezone.data,
            role="user",
        )
        user.login_at = pytz.utc.localize(datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"User {user.id} created")
        login_user(user)
        current_app.logger.info(f"User {current_user.id} logged in")

        # If users email address is in an unrecognised domain, ask them to create the organisation,
        # otherwise, add them to the existing organisation
        organisation = Organisation.query.filter_by(domain=current_user.email_address.split("@")[1]).first()
        if organisation is None:
            flash(
                "Looks like you're the first person here from your organisation.",
                "success",
            )
            return redirect(url_for("organisation.create"))
        else:
            current_user.organisation_id = organisation.id
            db.session.add(current_user)
            db.session.commit()
            flash(f"Welcome to {organisation.name}.", "success")
            return redirect(url_for("organisation.view"))

    return render_template("sign_up_form.html", title="Sign up", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data.lower().strip()).first()
        if user is None or not user.check_password(form.password.data):
            current_app.logger.warning("Failed login attempt")
            flash("Invalid email address or password.", "danger")
            return redirect(url_for("user.login"))
        login_user(user, remember=form.remember_me.data)
        user.login_at = pytz.utc.localize(datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"User {current_user.id} logged in")
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        flash(f"{current_user.name} logged in.", "success")
        return redirect(next_page)
    elif request.method == "GET" and current_user.is_authenticated:
        form.email_address.data = current_user.name
    return render_template("log_in_form.html", title="Log in", form=form)


@bp.route("/logout")
def logout():
    current_app.logger.info(f"User {current_user.id} logged out")
    name = current_user.name
    logout_user()
    flash(f"{name} logged out.", "success")
    return redirect(url_for("main.index"))


@bp.route("/users/<uuid:id>", methods=["GET"])
@login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def view(id):
    """Get a User with a specific ID."""
    user = User.query.get_or_404(str(id))

    # Prevent authenticated users from viewing users in other organisations
    if user.organisation_id != current_user.organisation_id:
        raise Forbidden()

    return render_template("view_user.html", title=user.name, user=user)


@bp.route("/users/<uuid:id>/edit", methods=["GET", "POST"])
@fresh_login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def edit(id):
    """Edit a User with a specific ID."""

    # Prevent authenticated users from editing other users
    if str(id) != current_user.id:
        raise Forbidden()

    form = UserForm()
    if form.validate_on_submit():
        current_user.email_address = form.email_address.data.lower().strip()
        current_user.name = form.name.data.strip()
        current_user.timezone = form.timezone.data
        current_user.updated_at = pytz.utc.localize(datetime.utcnow())
        db.session.add(current_user)
        db.session.commit()
        flash("Account changes have been saved.", "success")
        current_app.logger.info(f"User {current_user.id} updated account")
        return redirect(url_for("user.view", id=current_user.id))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email_address.data = current_user.email_address
        form.timezone.data = current_user.timezone
    return render_template("update_user.html", title="Edit user", form=form)


@bp.route("/users/<uuid:id>/delete", methods=["GET", "POST"])
@fresh_login_required
@limiter.limit("2 per second", key_func=lambda: current_user.id)
def delete(id):
    """Delete a User with a specific ID."""

    # Prevent authenticated users from deleting other users
    if str(id) != current_user.id:
        raise Forbidden()

    form = UserDeleteForm()

    if request.method == "GET":
        return render_template("delete_user.html", title="Delete account", form=form, user=current_user)
    elif request.method == "POST":
        current_app.logger.info(f"User {current_user.id} deleted account")
        db.session.delete(current_user)
        db.session.commit()
        flash(
            "Your account and all personal information has been permanently deleted.",
            "success",
        )
        return redirect(url_for("main.index"))
