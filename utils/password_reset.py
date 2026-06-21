from flask import session, request

from models.user import User
from models.password_reset_request import (
    PasswordResetRequest
)


def get_password_reset_requests():

    role = (
        session.get("role", "")
        .lower()
        .strip()
    )

    user_id = session.get("user_id")

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 20

    query = (
        PasswordResetRequest.query
        .join(
            User,
            User.id ==
            PasswordResetRequest.user_id
        )
        .order_by(
            PasswordResetRequest.created_at.desc()
        )
    )

    if role != "owner":

        query = query.filter(
            User.controller_id == user_id,
            PasswordResetRequest.status == "pending"
        )

    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
