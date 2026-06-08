from flask import Blueprint, request, session, redirect, render_template
from werkzeug.security import check_password_hash
from models.chamber import Chamber
from models.appointment import Appointment
from models.doctor import Doctor
from functools import wraps

chamber = Blueprint("chamber", __name__, url_prefix="/chamber")


# =========================
# LOGIN REQUIRED
# =========================
def chamber_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "chamber_id" not in session:
            return redirect("/chamber/login")

        return f(*args, **kwargs)

    return wrapper


# =========================
# LOGIN
# =========================
@chamber.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("chamber/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    chamber_user = Chamber.query.filter_by(username=username).first()

    if not chamber_user:
        return "Invalid Chamber"

    if not chamber_user.check_password(password):
        return "Wrong password"

    session.clear()
    session["chamber_id"] = chamber_user.id
    session["chamber_name"] = chamber_user.name

    return redirect("/chamber/dashboard")


# =========================
# DASHBOARD
# =========================
@chamber.route("/dashboard")
@chamber_login_required
def dashboard():

    cid = session["chamber_id"]

    doctors = Doctor.query.filter_by(chamber_id=cid).count()

    bookings = Appointment.query.filter_by(chamber_id=cid).count()

    recent = Appointment.query.filter_by(chamber_id=cid).order_by(Appointment.id.desc()).limit(10).all()

    return render_template(
        "chamber/dashboard.html",
        total_doctors=doctors,
        total_bookings=bookings,
        recent_bookings=recent
    )


# =========================
# LOGOUT
# =========================
@chamber.route("/logout")
def logout():
    session.clear()
    return redirect("/chamber/login")
