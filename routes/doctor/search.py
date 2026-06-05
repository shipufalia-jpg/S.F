from . import doctor_bp
from models import Doctor, Chamber
from flask import request, render_template


@doctor_bp.route("/search")
def search_doctors():

    query = request.args.get("q", "")

    area = request.args.get("area", "")

    doctors_query = Doctor.query

    # 🔍 NAME / SPECIALIZATION SEARCH
    if query:
        doctors_query = doctors_query.filter(
            (Doctor.name.ilike(f"%{query}%")) |
            (Doctor.specialization.ilike(f"%{query}%"))
        )

    doctors = doctors_query.all()

    # 🔍 AREA FILTER (IMPORTANT)
    if area:
        doctors = Doctor.query.join(Chamber).filter(
            Chamber.area.ilike(f"%{area}%")
        ).distinct().all()

    return render_template(
        "doctor/search.html",
        doctors=doctors,
        query=query,
        area=area
    )
