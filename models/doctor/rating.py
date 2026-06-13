from extensions import db
from datetime import datetime


class DoctorRating(db.Model):

    __tablename__ = "doctor_ratings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    ip_address = db.Column(
        db.String(50),
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
