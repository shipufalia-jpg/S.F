from flask import Blueprint, jsonify
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash

owner_tools = Blueprint("owner_tools", __name__)

@owner_tools.route("/create-owner")
def create_owner():

    existing_owner = User.query.filter_by(phone="999999999").first()

    if existing_owner:
        return jsonify({"status": "exists"})

    owner = User(
        name="Owner",
        phone="999999999",
        password=generate_password_hash("Owner123"),
        role="owner"
    )

    db.session.add(owner)
    db.session.commit()

    return jsonify({"status": "created"})
