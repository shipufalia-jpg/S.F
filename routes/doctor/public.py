from . import doctor_bp
from models.doctor import Doctor
from flask import render_template


@doctor_bp.route("/")
def doctor_list():

    doctors = Doctor.query.order_by(Doctor.id.desc()).all()

    return render_template(
        "doctor/list.html",
        doctors=doctors
    )
