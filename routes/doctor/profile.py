from . import doctor_bp
from models.doctor import Doctor
from flask import render_template
from utils.doctor import increase_view
from utils.rating import get_avg_rating


@doctor_bp.route("/<int:doctor_id>")
def doctor_profile(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    # 🔥 increase view safely
    increase_view(doctor)

    rating = get_avg_rating(doctor)

    return render_template(
        "doctor/profile.html",
        doctor=doctor,
        rating=rating
    )


@doctor_bp.route("/")
def doctors_home():
    return "DOCTORS HOME"

    doctors = Doctor.query.order_by(
        Doctor.verified.desc(),
        Doctor.views.desc()
    ).all()

    total_doctors = len(doctors)

    verified_doctors = Doctor.query.filter_by(
        verified=True
    ).count()

    total_views = sum(
        doctor.views or 0
        for doctor in doctors
    )

    return render_template(
        "doctor/home.html",
        doctors=doctors,
        total_doctors=total_doctors,
        verified_doctors=verified_doctors,
        total_views=total_views
    )
