from extensions import db
from datetime import datetime, timedelta


class PhoneOTP(db.Model):

    __tablename__ = "phone_otps"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    phone = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )

    otp_code = db.Column(
        db.String(10),
        nullable=False
    )

    purpose = db.Column(
        db.String(50),
        default="appointment",
        index=True
    )
    # appointment
    # login
    # reset_password

    is_verified = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
