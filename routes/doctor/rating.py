from . import doctor_bp
from flask import request, redirect
from models import DoctorRating, db


@doctor_bp.route("/rate/<int:doctor_id>", methods=["POST"])
def rate_doctor(doctor_id):

    rating_value = int(request.form.get("rating"))

    ip = request.remote_addr

    existing = DoctorRating.query.filter_by(
        doctor_id=doctor_id,
        ip_address=ip
    ).first()

    if existing:
        existing.rating = rating_value
    else:
        new_rating = DoctorRating(
            doctor_id=doctor_id,
            rating=rating_value,
            ip_address=ip
        )
        db.session.add(new_rating)

    db.session.commit()

    return redirect(f"/doctors/{doctor_id}")
