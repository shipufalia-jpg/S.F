from . import doctor_bp
from flask import request, redirect, flash
from models.doctor import DoctorRating
from extensions import db


@doctor_bp.route("/rate/<int:doctor_id>", methods=["POST"])
def rate_doctor(doctor_id):

    try:
        rating_value = int(
            request.form.get("rating", 0)
        )

        if rating_value not in [1, 2, 3, 4, 5]:
            flash("Invalid rating.", "danger")
            return redirect(f"/doctors/{doctor_id}")

        ip = request.remote_addr

        existing = DoctorRating.query.filter_by(
            doctor_id=doctor_id,
            ip_address=ip
        ).first()

        if existing:
            existing.rating = rating_value
        else:
            db.session.add(
                DoctorRating(
                    doctor_id=doctor_id,
                    rating=rating_value,
                    ip_address=ip
                )
            )

        db.session.commit()

        flash(
            "Rating submitted successfully.",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash(
            "Something went wrong.",
            "danger"
        )

    return redirect(
        f"/doctors/{doctor_id}"
        )
