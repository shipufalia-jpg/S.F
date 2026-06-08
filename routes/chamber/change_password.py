from flask import Blueprint, request, session, redirect
from models.chamber import Chamber
from extensions import db
from werkzeug.security import check_password_hash, generate_password_hash

chamber_auth = Blueprint("chamber_auth", __name__)

@chamber_auth.route("/change-password", methods=["POST"])
def change_password():

    chamber_id = session.get("chamber_id")

    chamber = Chamber.query.get(chamber_id)

    current = request.form.get("current_password")
    new_pass = request.form.get("new_password")

    if not chamber.check_password(current):
        return "Wrong current password"

    chamber.password_hash = generate_password_hash(new_pass)

    db.session.commit()

    return "Password updated successfully"
