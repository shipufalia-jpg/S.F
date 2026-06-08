from functools import wraps
from flask import session, redirect

# =====================================================
# CHAMBER LOGIN CHECK
# =====================================================
def chamber_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "chamber_id" not in session:
            return redirect("/chamber/login")

        return f(*args, **kwargs)

    return wrapper
