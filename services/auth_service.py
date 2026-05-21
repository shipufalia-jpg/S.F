def role_redirect():
    role = session.get('role')

    if not role:
        return "/auth/login"

    allowed_roles = ["owner", "super_admin", "admin", "worker", "user"]

    if role not in allowed_roles:
        session.clear()
        return "/auth/login"

    return {
        "owner": "/owner/dashboard",
        "super_admin": "/super/dashboard",
        "admin": "/admin/dashboard",
        "worker": "/worker/dashboard",
        "user": "/user/dashboard"
    }.get(role)
