from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional


class ThingForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            InputRequired(message="Enter a name"),
            Length(max=32, message="Name must be 32 characters or fewer"),
        ],
        description="Must be 32 characters or fewer.",
    )
    colour = RadioField(
        "Colour",
        validators=[InputRequired(message="Select a colour")],
        choices=[
            ("red", "Red"),
            ("green", "Green"),
            ("blue", "Blue"),
            ("yellow", "Yellow"),
            ("orange", "Orange"),
            ("purple", "Purple"),
            ("black", "Black"),
            ("white", "White"),
        ],
    )


class ThingFilterForm(FlaskForm):
    query = StringField("Search", validators=[Optional()])
    sort = SelectField(
        "Sort by",
        validators=[InputRequired()],
        choices=[
            ("created_at", "Most recent"),
            ("name", "Name"),
            ("colour", "Colour"),
            ("user_id", "Owner"),
        ],
        default="created_at",
    )
    per_page = SelectField(
        "Items per page",
        validators=[InputRequired()],
        choices=[(10, "10"), (20, "20"), (40, "40")],
        default=20,
    )
    colour = RadioField(
        "Colour",
        validators=[Optional()],
        choices=[
            ("", "All"),
            ("red", "Red"),
            ("green", "Green"),
            ("blue", "Blue"),
            ("yellow", "Yellow"),
            ("orange", "Orange"),
            ("purple", "Purple"),
            ("black", "Black"),
            ("white", "White"),
        ],
        default="",
    )


class ThingDeleteForm(FlaskForm):
    pass
