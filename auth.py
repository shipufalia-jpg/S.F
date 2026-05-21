from functools import wraps
from flask import session, redirect, url_for

def role_required(required_role):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            role = session.get('role')
            user_id = session.get('user_id')

            # 🔐 login check
            if not role or not user_id:
                return redirect(url_for('auth.login'))

            # 🚫 role check
            if role != required_role:
                return "Access Denied ❌", 403

            return func(*args, **kwargs)

        return inner
    return wrapper