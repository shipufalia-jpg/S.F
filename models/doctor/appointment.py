from extensions import db
from datetime import datetime

class Appointment(db.Model):

    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    chamber_id = db.Column(db.Integer, db.ForeignKey("chambers.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"))

    patient_name = db.Column(db.String(150))
    patient_phone = db.Column(db.String(20))

    booking_date = db.Column(db.Date)
    booking_time = db.Column(db.String(20))

    status = db.Column(db.String(20), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
