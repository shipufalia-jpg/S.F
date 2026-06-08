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

def can_create_chamber(user):
    return user.role in ["owner", "super_admin", "admin"]


def can_view_chamber(user, chamber):
    if user.role == "owner":
        return True

    if user.role == "super_admin":
        return chamber.super_admin_id == user.id

    if user.role == "admin":
        return chamber.admin_id == user.id

    if user.role == "chamber":
        return chamber.id == user.id

    return False


def can_block_or_delete(user):
    return user.role == "owner"
