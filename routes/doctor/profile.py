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
