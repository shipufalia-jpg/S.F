from flask import Blueprint, request, render_template, jsonify
from models.doctor.doctor import Doctor
from models.chamber_profile import ChamberProfile

search_bp = Blueprint("search_bp", __name__)


# ==========================================
# PAGE (UI LOAD)
# ==========================================
@search_bp.route("/search-page")
def search_page():
    return render_template("chamber/search.html")


# ==========================================
# API (SEARCH DATA)
# ==========================================
@search_bp.route("/search")
def search():

    q = request.args.get("q", "").strip()
    type_ = request.args.get("type", "all")

    results = []

    # =========================
    # DOCTOR SEARCH
    # =========================
    doctors = Doctor.query.filter(
        Doctor.name.contains(q)
    ).all()

    for d in doctors:
        results.append({
            "name": d.name,
            "area": d.hospital,
            "type": "Doctor"
        })

    # =========================
    # CHAMBER SEARCH
    # =========================
    chambers = ChamberProfile.query.filter(
        ChamberProfile.chamber_name.contains(q)
    ).all()

    for c in chambers:
        results.append({
            "name": c.chamber_name,
            "area": c.area,
            "type": "Chamber"
        })

    # =========================
    # FILTER SYSTEM
    # =========================
    if type_ != "all":
        results = [
            r for r in results if r["type"].lower() == type_
        ]

    return jsonify(results)
