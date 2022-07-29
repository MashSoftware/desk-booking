from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length, ValidationError

from app.models import Organisation


class OrganisationForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            InputRequired(message="Enter a name"),
        ],
        description="The name of the organisation, company, business or institution",
    )

    domain = StringField(
        "Domain name",
        validators=[
            InputRequired(message="Enter a domain name"),
            Length(max=255, message="Domain name must be 255 characters or fewer"),
        ],
    )

    def validate_domain(self, domain):
        # If organisation has changed domains, prevent duplication with another organisation
        if domain.data != current_user.organisation.domain:
            org = Organisation.query.filter_by(domain=domain.data).first()
            if org is not None:
                raise ValidationError("Domain name is already in use")


class OrganisationDeleteForm(FlaskForm):
    pass
