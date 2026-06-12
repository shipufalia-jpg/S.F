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

    # rating save code
    pass
