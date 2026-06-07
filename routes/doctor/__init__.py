from flask import Blueprint

doctor_bp = Blueprint(
    "doctor",
    __name__,
    url_prefix="/doctors"
)
from . import public, admin, profile, search, rating
