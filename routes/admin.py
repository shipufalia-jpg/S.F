from flask import (
    Blueprint,
    render_template,
    session,
    jsonify,
    request,
    flash,
    redirect,
    url_for
)

import json

from sqlalchemy.orm import (
    load_only,
    joinedload
)

from werkzeug.security import (
    generate_password_hash
)

from extensions import (
    db,
    limiter
)

from utils.decorators import (
    admin_required,
    role_required
)

from utils.activity_logger import (
    log_activity
)

from utils.password_validator import (
    validate_password
)

from utils.password_reset import (
    get_password_reset_requests,
    can_manage_reset_request
)

from models.user import User
from models.profile import Profile
from models.chat import Chat
from models.booking import Booking
from models.work_model import Work
from models.notification import Notification
from models.work_application import WorkApplication
from models.password_reset_request import PasswordResetRequest


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# ================= RESPONSE =================

def success(data=None, message="OK"):
    return jsonify({"success": True, "message": message, "data": data}), 200

def error(msg="Error", code=400):
    return jsonify({"success": False, "message": msg}), code


# ================= DASHBOARD =================

@admin_bp.route("/")
@admin_required
def dashboard():

    user_id = session.get("user_id")

    total = User.query.filter_by(controller_id=user_id).count()
    active = User.query.filter_by(controller_id=user_id, status="active").count()
    blocked = User.query.filter_by(controller_id=user_id, status="blocked").count()

    return render_template(
        "admin/dashboard.html",
        total=total,
        active=active,
        blocked=blocked,
        user_id=user_id
    )


# ================= USERS =================

@admin_bp.route("/users")
@admin_required
def users():

    user_id = session.get("user_id")

    page = max(
        request.args.get("page", 1, type=int),
        1
    )

    per_page = min(
        max(
            request.args.get(
                "limit",
                20,
                type=int
            ),
            1
        ),
        20
    )

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()[:50]

    query = (
        User.query
        .filter_by(
            controller_id=user_id
        )
        .options(
            load_only(
                User.id,
                User.name,
                User.status
            )
        )
    )

    if search:
        query = query.filter(
            User.name.ilike(
                f"%{search}%"
            )
        )

    users = query.order_by(
        User.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return success({
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "status": u.status
            }
            for u in users.items
        ],

        "pagination": {
            "total": users.total,
            "pages": users.pages,
            "current": users.page,
            "per_page": users.per_page,
            "has_next": users.has_next,
            "has_prev": users.has_prev
        }
    })


# ================= USER STATUS =================

@admin_bp.route(
    "/user/<int:id>/status",
    methods=["POST"]
)
@admin_required
def update_user_status(id):

    user = User.query.filter_by(
        id=id,
        controller_id=session.get(
            "user_id"
        )
    ).first_or_404()

    data = (
        request.get_json(
            silent=True
        ) or {}
    )

    status = (
        data.get(
            "status",
            ""
        ).strip().lower()
    )

    allowed_status = {
        "active",
        "blocked"
    }

    if status not in allowed_status:
        return error(
            "Invalid status",
            400
        )

    if user.status == status:
        return success(
            message=(
                f"User already "
                f"{status}"
            )
        )

    try:

        old_status = user.status

        user.status = status

        log_activity(
            actor_id=session.get(
                "user_id"
            ),
            target_id=user.id,
            action=(
                f"user_status_"
                f"{status}"
            ),
            role=session.get(
                "role"
            ),
            meta={
                "old_status":
                    old_status,
                "new_status":
                    status
            }
        )

        db.session.commit()

        return success(
            message=(
                f"User status "
                f"updated to "
                f"{status}"
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            "User Status Error:",
            e
        )

        return error(
            "Unable to update status",
            500
        )


# ================= BULK ACTION =================

@admin_bp.route(
    "/users/bulk",
    methods=["POST"]
)
@admin_required
@limiter.limit("5 per minute")
def bulk_users():

    data = (
        request.get_json(
            silent=True
        ) or {}
    )

    ids = data.get(
        "ids",
        []
    )

    action = (
        data.get(
            "action",
            ""
        ).strip().lower()
    )

    if action not in {
        "block",
        "unblock"
    }:
        return error(
            "Invalid action",
            400
        )

    if (
        not isinstance(ids, list)
        or not ids
        or len(ids) > 100
    ):
        return error(
            "Invalid user list",
            400
        )

    try:

        users = (
            User.query
            .filter(
                User.id.in_(ids),
                User.controller_id ==
                session.get("user_id")
            )
            .all()
        )

        if not users:
            return error(
                "No users found",
                404
            )

        new_status = (
            "blocked"
            if action == "block"
            else "active"
        )

        updated_count = 0

        for user in users:

            if user.status == new_status:
                continue

            old_status = user.status

            user.status = new_status

            log_activity(
                actor_id=session.get(
                    "user_id"
                ),
                target_id=user.id,
                action=f"bulk_{action}",
                role=session.get(
                    "role"
                ),
                meta={
                    "old_status":
                        old_status,
                    "new_status":
                        new_status
                }
            )

            updated_count += 1

        db.session.commit()

        return success(
            message=(
                f"{updated_count} users "
                f"updated successfully"
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            "Bulk User Error:",
            e
        )

        return error(
            "Bulk action failed",
            500
        )

# ================= ANALYTICS =================

@admin_bp.route("/analytics")
@admin_required
def analytics():

    user_id = session.get("user_id")

    total = User.query.filter_by(controller_id=user_id).count()
    active = User.query.filter_by(controller_id=user_id, status="active").count()
    blocked = User.query.filter_by(controller_id=user_id, status="blocked").count()

    bookings = Booking.query.join(User)\
        .filter(User.controller_id == user_id).count()

    works = Work.query.filter_by(created_by=user_id).count()

    return success({
        "users": {
            "total": total,
            "active": active,
            "blocked": blocked
        },
        "bookings": bookings,
        "works": works
    })

# ================= USERS PAGE (HTML) =================
@admin_bp.route("/users-page")
@admin_required
def users_page():

    admin_id = session.get("user_id")

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()[:50]

    query = (
        User.query
        .filter_by(
            controller_id=admin_id,
            is_deleted=False
        )
        .options(
            load_only(
                User.id,
                User.name,
                User.status,
                User.created_at
            )
        )
    )

    if search:
        query = query.filter(
            User.name.ilike(
                f"%{search}%"
            )
        )

    users = (
        query
        .order_by(
            User.id.desc()
        )
        .paginate(
            page=page,
            per_page=20,
            error_out=False
        )
    )

    return render_template(
        "admin/users.html",
        users=users.items,
        pagination=users,
        search=search
    )
# ================= USERS API (JSON) =================
@admin_bp.route("/api/users")
@admin_required
def users_api():

    user_id = session.get("user_id")

    page = max(
        request.args.get(
            "page",
            1,
            type=int
        ),
        1
    )

    per_page = min(
        max(
            request.args.get(
                "limit",
                20,
                type=int
            ),
            1
        ),
        20
    )

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()[:50]

    query = (
        User.query
        .filter_by(
            controller_id=user_id
        )
        .options(
            load_only(
                User.id,
                User.name,
                User.status
            )
        )
    )

    if search:
        query = query.filter(
            User.name.ilike(
                f"%{search}%"
            )
        )

    users = (
        query
        .order_by(User.id.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return success({
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "status": u.status
            }
            for u in users.items
        ],
        "pagination": {
            "total": users.total,
            "pages": users.pages,
            "current": users.page,
            "per_page": users.per_page,
            "has_next": users.has_next,
            "has_prev": users.has_prev
        }
    })
# ================= USER DETAILS (POPUP) =================

@admin_bp.route("/user/<int:user_id>")
@admin_required
def get_user(user_id):

    admin_id = session.get("user_id")

    user = (
        User.query
        .options(
            joinedload(User.profile)
        )
        .filter_by(
            id=user_id,
            controller_id=admin_id,
            is_deleted=False
        )
        .first_or_404()
    )

    profile = user.profile

    # ================= RECENT WORKS =================
    works = (
        Work.query
        .filter_by(user_id=user.id)
        .order_by(Work.id.desc())
        .limit(10)
        .all()
    )

    # ================= GALLERY =================
    gallery_images = []

    if profile and profile.gallery:
        try:
            gallery_images = json.loads(
                profile.gallery
            )
        except json.JSONDecodeError:
            gallery_images = []

    # ================= COUNTS =================

    total_works = (
        Work.query
        .filter_by(user_id=user.id)
        .count()
    )

    total_gallery = len(
        gallery_images
    )

    total_applications = (
        WorkApplication.query
        .filter_by(user_id=user.id)
        .count()
    )

    total_chats = (
        Chat.query.filter(
            (Chat.sender_id == user.id) |
            (Chat.receiver_id == user.id)
        )
        .count()
    )

    # ================= STATUS =================

    online_status = (
        "Online"
        if user.is_online
        else "Offline"
    )

    last_seen = (
        user.last_seen.strftime(
            "%d %b %Y %I:%M %p"
        )
        if user.last_seen
        else None
    )

    joined_date = (
        user.created_at.strftime(
            "%d %b %Y"
        )
        if user.created_at
        else None
    )

    # ================= PROFILE IMAGE =================

    profile_image = (
        profile.profile_img
        if (
            profile
            and profile.profile_img
        )
        else "/static/default.png"
    )

    return render_template(
        "admin/user_profile.html",

        user=user,
        profile=profile,

        works=works,

        gallery_images=gallery_images,

        total_works=total_works,
        total_gallery=total_gallery,
        total_applications=total_applications,
        total_chats=total_chats,

        online_status=online_status,
        last_seen=last_seen,
        joined_date=joined_date,

        profile_image=profile_image
    )

@admin_bp.route("/chambers-control")
@role_required(
    "admin",
    "owner",
    "super_admin"
)
def chambers_control():

    return render_template(
        "admin/chambers_control.html"
)



@admin_bp.route("/password-resets")
@role_required(
    "admin",
    "owner",
    "super_admin"
)
def password_resets():

    try:

        requests = (
            get_password_reset_requests()
        )

        return render_template(
            "password_resets.html",
            requests=requests
        )

    except Exception as e:

        print(
            "Password Reset List Error:",
            e
        )

        flash(
            "Unable to load requests.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )



from datetime import datetime, UTC

@admin_bp.route(
    "/password-resets/<int:req_id>",
    methods=["GET", "POST"]
)
@role_required(
    "admin",
    "owner",
    "super_admin"
)
@limiter.limit("5 per minute")
def reset_user_password(req_id):

    req = db.session.get(
        PasswordResetRequest,
        req_id
    )

    if not req:
        flash(
            "Request not found.",
            "danger"
        )
        return redirect(
            url_for(
                "admin.password_resets"
            )
        )

    if not can_manage_reset_request(req):
        flash(
            "Permission denied.",
            "danger"
        )
        return redirect(
            url_for(
                "admin.password_resets"
            )
        )

    if req.status != "pending":
        flash(
            "Request already processed.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.password_resets"
            )
        )

    user = db.session.get(
        User,
        req.user_id
    )

    if not user:
        flash(
            "User not found.",
            "danger"
        )
        return redirect(
            url_for(
                "admin.password_resets"
            )
        )

    if request.method == "GET":

        return render_template(
            "admin_reset_password.html",
            req=req,
            user=user
        )

    new_password = (
        request.form.get(
            "password",
            ""
        ).strip()
    )

    validation_error = (
        validate_password(
            new_password
        )
    )

    if validation_error:

        flash(
            validation_error,
            "danger"
        )

        return redirect(
            url_for(
                "admin.reset_user_password",
                req_id=req.id
            )
        )

    try:

        user.password = (
            generate_password_hash(
                new_password,
                method="pbkdf2:sha256",
                salt_length=16
            )
        )

        user.must_change_password = True

        req.status = "completed"

        req.handled_by = (
            session.get(
                "user_id"
            )
        )

        req.processed_at = (
            datetime.now(UTC)
        )

        # Activity Log
        log_activity(
            actor_id=session.get(
                "user_id"
            ),
            target_id=user.id,
            action="password_reset",
            role=session.get(
                "role"
            ),
            meta={
                "request_id": req.id
            }
        )

        # Optional Notification
        notification = Notification(
            user_id=user.id,
            title="Password Reset",
            message=(
                "Your password was "
                "reset by admin."
            )
        )

        db.session.add(
            notification
        )

        db.session.commit()

        flash(
            "Temporary password set successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "Reset Password Error:",
            str(e)
        )

        flash(
            "Something went wrong.",
            "danger"
        )

    return redirect(
        url_for(
            "admin.password_resets"
        )
    )
