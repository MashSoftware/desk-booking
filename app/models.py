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
    name = db.Column(db.String, nullable=False, index=True)
    email_address = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password = db.Column(db.LargeBinary, nullable=False)
    timezone = db.Column(db.String, nullable=False, server_default="UTC")
    organisation_id = db.Column(
        UUID,
        db.ForeignKey("organisation.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    role = db.Column(db.String, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Methods
    def __init__(self, name, email_address, password, timezone, role):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.email_address = email_address.lower().strip()
        self.timezone = timezone
        self.role = role
        self.created_at = pytz.utc.localize(datetime.utcnow())
        self.set_password(password)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("UTF-8"), self.password)


@login.user_loader
def load_user(id):
    return User.query.get(id)


class Organisation(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    domain = db.Column(db.String(255), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    users = db.relationship("User", backref="organisation", lazy=True, passive_deletes=True)

    # Methods
    def __init__(self, name, domain):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.domain = domain.lower().strip()
        self.created_at = pytz.utc.localize(datetime.utcnow())
