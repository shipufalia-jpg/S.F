# =========================================
# permissions.py
# =========================================

from flask import session
from models.user import User


# =========================================
# CURRENT USER
# =========================================

def current_user_id():
    return session.get("user_id")


def current_role():
    return session.get("role")


# =========================================
# ROLE CHECK
# =========================================

def is_user():
    return current_role() == "user"


def is_admin():
    return current_role() == "admin"


def is_super_admin():
    return current_role() == "super_admin"


def is_owner():
    return current_role() == "owner"


# =========================================
# OWNER FULL ACCESS
# =========================================

def owner_has_full_access():
    return is_owner()


# =========================================
# ADMIN CONTROL
# admin controls own users
# =========================================

def admin_can_manage_user(user):

    if not user:
        return False

    if not is_admin():
        return False

    return user.created_by == current_user_id()


# =========================================
# SUPER ADMIN CONTROL
# super admin controls admins
# created by him
# =========================================

def super_admin_can_manage_admin(admin):

    if not admin:
        return False

    if not is_super_admin():
        return False

    return (
        admin.role == "admin"
        and
        admin.created_by == current_user_id()
    )


# =========================================
# SUPER ADMIN USER CONTROL
# controls all users under his admins
# =========================================

def super_admin_can_manage_user(user):

    if not user:
        return False

    if not is_super_admin():
        return False

    # find admins created by super admin
    admins = User.query.filter_by(
        role="admin",
        created_by=current_user_id(),
        is_deleted=False
    ).all()

    admin_ids = [a.id for a in admins]

    return user.created_by in admin_ids


# =========================================
# MAIN CONTROL SYSTEM
# =========================================

def can_manage_user(user):

    if not user:
        return False

    # OWNER
    if is_owner():
        return True

    # SUPER ADMIN
    if is_super_admin():

        # can manage own admins
        if user.role == "admin":
            return super_admin_can_manage_admin(user)

        # can manage users under own admins
        return super_admin_can_manage_user(user)

    # ADMIN
    if is_admin():
        return admin_can_manage_user(user)

    return False


# =========================================
# BOOKING CONTROL
# =========================================

def can_manage_booking(booking):

    if not booking:
        return False

    # OWNER FULL ACCESS
    if is_owner():
        return True

    booking_user = booking.user

    if not booking_user:
        return False

    # ADMIN
    if is_admin():
        return booking_user.created_by == current_user_id()

    # SUPER ADMIN
    if is_super_admin():

        admins = User.query.filter_by(
            role="admin",
            created_by=current_user_id(),
            is_deleted=False
        ).all()

        admin_ids = [a.id for a in admins]

        return booking_user.created_by in admin_ids

    return False