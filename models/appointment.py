from extensions import db
from datetime import datetime


class Appointment(db.Model):

    __tablename__ = "appointments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    chamber_id = db.Column(
        db.Integer,
        db.ForeignKey("chambers.id"),
        nullable=False,
        index=True
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    patient_name = db.Column(
        db.String(150),
        nullable=False
    )

    patient_phone = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )

    phone_verified = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    status = db.Column(
        db.String(20),
        default="pending",
        index=True
    )
    # pending
    # confirmed
    # completed
    # cancelled

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    doctor = db.relationship("Doctor", backref="appointments")
