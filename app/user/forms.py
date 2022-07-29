import pytz
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, ValidationError

from app.models import User

disallowed_domains = [
    "aol",
    "gmail",
    "googlemail",
    "hotmail",
    "icloud",
    "live",
    "msn",
    "outlook",
    "pm",
    "proton",
    "protonmail",
    "yahoo",
]


class SignupForm(FlaskForm):
    tz_tuples = []
    for tz in pytz.common_timezones:
        tz_tuples.append((tz, tz.replace("_", " ")))

    name = StringField("Full name", validators=[InputRequired("Enter your full name")])

    email_address = StringField(
        "Organisation email address",
        validators=[
            InputRequired(message="Enter your email address"),
            Email(granular_message=True, check_deliverability=True),
            Length(max=256, message="Email address must be 256 characters or fewer"),
        ],
        description="Your organisation, company, business or institution email address.",
    )
    password = PasswordField(
        "Create a password",
        validators=[
            InputRequired(message="Enter a password"),
            Length(min=8, max=72, message="Password must be between 8 and 72 characters"),
        ],
        description="Must be between 8 and 72 characters.",
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            InputRequired(message="Confirm your password"),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    timezone = SelectField(
        "Timezone",
        validators=[InputRequired(message="Select a timezone")],
        choices=tz_tuples,
        default="Europe/London",
    )

    def validate_email_address(self, email_address):
        # Prevent users from signing up with personal email addresses
        for domain in disallowed_domains:
            if domain in email_address.data.split("@")[1]:
                raise ValidationError("Email address must not be a personal address.")

        # Prevent users from signing up with an email address that is already in use
        user = User.query.filter_by(email_address=email_address.data).first()
        if user is not None:
            raise ValidationError("Email address is already in use, please log in")


class LoginForm(FlaskForm):
    email_address = StringField(
        "Email address",
        validators=[
            InputRequired(message="Enter an email address"),
            Email(granular_message=True, check_deliverability=True),
            Length(max=256, message="Email address must be 256 characters or fewer"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Enter a password"),
            Length(min=8, max=72, message="Password must be between 8 and 72 characters"),
        ],
        description="Must be between 8 and 72 characters.",
    )
    remember_me = BooleanField("Remember me", validators=[Optional()])


class UserForm(FlaskForm):
    tz_tuples = []
    for tz in pytz.common_timezones:
        tz_tuples.append((tz, tz.replace("_", " ")))

    name = StringField("Full name", validators=[InputRequired("Enter your full name")])

    email_address = StringField(
        "Organisation email address",
        validators=[
            InputRequired(message="Enter your email address"),
            Email(granular_message=True, check_deliverability=True),
            Length(max=255, message="Email address must be 255 characters or fewer"),
        ],
        description="Your organisation, company, business or institution email address.",
    )

    timezone = SelectField(
        "Timezone",
        validators=[InputRequired(message="Select a timezone")],
        choices=tz_tuples,
        default="Europe/London",
    )

    def validate_email_address(self, email_address):
        # If user has changed email address, prevent duplication with another user
        if email_address.data != current_user.email_address:
            user = User.query.filter_by(email_address=email_address.data).first()
            if user is not None:
                raise ValidationError("Email address is already in use")

        # Prevent users from changing email address domains outside of their organisation domain
        if email_address.data.split("@")[1] != current_user.organisation.domain:
            raise ValidationError(f"Email address must be in the {current_user.organisation.domain} domain")


class UserDeleteForm(FlaskForm):
    pass
