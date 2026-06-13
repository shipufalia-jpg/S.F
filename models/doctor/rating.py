from . import doctor_bp
from flask import (
    render_template,
    request,
    redirect,
    flash,
    url_for
)

from models.doctor import DoctorRating
from extensions import db


@doctor_bp.route("/<int:doctor_id>/rating")
def rating_page(doctor_id):

    return render_template(
        "doctor/rating.html",
        doctor_id=doctor_id
    )


@doctor_bp.route(
    "/rate/<int:doctor_id>",
    methods=["POST"]
)
def rate_doctor(doctor_id):

    rating = request.form.get("rating")

    if not rating:
        flash(
            "Please select a rating.",
            "danger"
        )
        return redirect(
            url_for(
                "doctor.rating_page",
                doctor_id=doctor_id
            )
        )

    # একই IP থেকে একবারের বেশি rating না দিতে চাইলে
    existing_rating = DoctorRating.query.filter_by(
        doctor_id=doctor_id,
        ip_address=request.remote_addr
    ).first()

    if existing_rating:
        flash(
            "You have already rated this doctor.",
            "warning"
        )
        return redirect(
            url_for(
                "doctor.rating_page",
                doctor_id=doctor_id
            )
        )

    new_rating = DoctorRating(
        doctor_id=doctor_id,
        rating=int(rating),
        ip_address=request.remote_addr
    )

    db.session.add(new_rating)
    db.session.commit()

    flash(
        "Rating submitted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "doctor.rating_page",
            doctor_id=doctor_id
        )
    )
