from flask import session
from extensions import db


def increase_view(doctor):

    key = f"doctor_view_{doctor.id}"

    if not session.get(key):

        doctor.views += 1

        session[key] = True

        db.session.commit()
