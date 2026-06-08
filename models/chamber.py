from extensions import db
from datetime import datetime
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


class Chamber(db.Model):

    __tablename__ = "chambers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    phone = db.Column(
        db.String(20)
    )

    address = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(20),
        default="active",
        nullable=False,
        index=True
    )

    created_by_admin_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    controller_admin_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    super_admin_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    last_login = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
  )
