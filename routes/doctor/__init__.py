from flask import Blueprint

doctor_bp = Blueprint(
    "doctor",
    __name__,
    url_prefix="/doctors"
)

from . import public
from . import profile
from . import search
from . import rating
from . import admin
