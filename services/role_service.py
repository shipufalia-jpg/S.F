# services/role_service.py

from flask import session


def can_manage_booking():
    role = session.get('role')
    return role in ["owner", "super_admin", "admin"]


def is_owner():
    return session.get('role') == "owner"


def is_super_admin():
    return session.get('role') == "super_admin"


def is_admin():
    return session.get('role') == "admin"