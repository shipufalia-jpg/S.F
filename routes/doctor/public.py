from . import doctor_bp
from models.doctor import Doctor
from flask import render_template, request

# ==========================================
# DOCTOR LIST
# ==========================================

@doctor_bp.route("/list")
def doctor_list():

    q = request.args.get("q", "").strip()

    doctors = Doctor.query

    if q:
        doctors = doctors.filter(
            db.or_(
                Doctor.name.ilike(f"%{q}%"),
                Doctor.specialization.ilike(f"%{q}%"),
                Doctor.hospital.ilike(f"%{q}%")
            )
        )

    doctors = doctors.order_by(
        Doctor.id.desc()
    ).all()

    DEFAULT_COVER = "https://images.unsplash.com/photo-1580281658629-0a2d1a3c3d9c?auto=format&fit=crop&w=1200&q=80"

    return render_template(
        "doctor/list.html",
        doctors=doctors
    )
