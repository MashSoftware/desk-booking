import uuid
from datetime import datetime

import bcrypt
import pytz
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = "user_account"

    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String(256), nullable=False, unique=True, index=True)
    password = db.Column(db.LargeBinary, nullable=False)
    timezone = db.Column(db.String, nullable=False, server_default="UTC")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    things = db.relationship("Thing", backref="user", lazy=True, passive_deletes=True)

    # Methods
    def __init__(self, name, email_address, password, timezone):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.email_address = email_address.lower().strip()
        self.timezone = timezone
        self.created_at = pytz.utc.localize(datetime.utcnow())
        self.set_password(password)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("UTF-8"), self.password)


@login.user_loader
def load_user(id):
    return User.query.get(id)


class Thing(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    user_id = db.Column(
        UUID,
        db.ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(32), nullable=False, index=True)
    colour = db.Column(db.String(), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Methods
    def __init__(self, name, colour, user_id):
        self.id = str(uuid.uuid4())
        self.name = name.title().strip()
        self.colour = colour
        self.user_id = user_id
        self.created_at = pytz.utc.localize(datetime.utcnow())
