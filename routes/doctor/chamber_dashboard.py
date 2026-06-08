from flask import Blueprint, session, redirect, render_template
from functools import wraps

from models.appointment import Appointment
from models.doctor import Doctor

chamber = Blueprint(
    "chamber",
    __name__,
    url_prefix="/chamber"
)

# =====================================================
# LOGIN REQUIRED (CHAMBER ONLY)
# =====================================================
def chamber_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "chamber_id" not in session:
            return redirect("/chamber/login")

        return f(*args, **kwargs)

    return wrapper


# =====================================================
# DASHBOARD
# =====================================================
@chamber.route("/dashboard")
@chamber_login_required
def dashboard():

    chamber_id = session.get("chamber_id")

    total_doctors = Doctor.query.filter_by(
        chamber_id=chamber_id
    ).count()

    total_bookings = Appointment.query.filter_by(
        chamber_id=chamber_id
    ).count()

    recent_bookings = Appointment.query.filter_by(
        chamber_id=chamber_id
    ).order_by(Appointment.id.desc()).limit(10).all()

    return render_template(
        "chamber/dashboard.html",
        total_doctors=total_doctors,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )
