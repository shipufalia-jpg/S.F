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

appointment_date = db.Column(
    db.Date,
    nullable=True
)

appointment_time = db.Column(
    db.String(20),
    nullable=True
)

notes = db.Column(
    db.Text,
    nullable=True
)

confirmed_date = db.Column(
    db.Date,
    nullable=True
)

confirmed_time = db.Column(
    db.String(20),
    nullable=True
)

confirmation_note = db.Column(
    db.Text,
    nullable=True
)

user_id = db.Column(
    db.Integer,
    db.ForeignKey("user.id"),
    nullable=True,
    index=True
)

user = db.relationship(
    "User",
    backref="appointments"
)

chamber = db.relationship(
    "Chamber",
    backref="appointments"
)

doctor = db.relationship(
    "Doctor",
    backref="appointments"
)
