from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from models.chamber import Chamber
from extensions import db
from datetime import datetime

chamber_auth = Blueprint(
    "chamber_auth",
    __name__,
    url_prefix="/chamber"
)

# =====================================================
# LOGIN
# =====================================================
@chamber_auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("chamber/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "All fields required"

    chamber = Chamber.query.filter_by(username=username).first()

    if not chamber:
        return "Invalid Chamber"

    if chamber.status != "active":
        return "Chamber blocked"

    if not check_password_hash(chamber.password_hash, password):
        return "Wrong password"

    session.clear()

    session["chamber_id"] = chamber.id
    session["chamber_name"] = chamber.name

    chamber.last_login = datetime.utcnow()

    db.session.commit()

    return redirect(url_for("chamber.dashboard"))
