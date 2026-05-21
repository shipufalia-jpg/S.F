from functools import wraps
from flask import session, redirect, url_for

# ================= LOGIN REQUIRED =================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return wrapper


# ================= ADMIN + SUPER ADMIN =================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("role") not in ["admin", "super_admin"]:
            return "Unauthorized", 403

        return f(*args, **kwargs)

    return wrapper


# ================= SUPER ADMIN ONLY =================
def super_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get("role") != "super_admin":
            return "Only Super Admin allowed", 403

        return f(*args, **kwargs)

    return wrapper