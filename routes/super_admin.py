from flask import (
    Blueprint,
    session,
    request,
    render_template,
    flash,
    redirect,
    url_for
)

from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload
import json

from extensions import db, socketio

from models.user import User
from models.profile import Profile
from models.chat import Chat
from models.work_application import WorkApplication
from models.activity_log import ActivityLog
from models.work_model import Work

from services.logger import log_activity


# =========================================================
# BLUEPRINT
# =========================================================

super_admin = Blueprint(
    "super_admin",
    __name__,
    url_prefix="/super"
)


# =========================================================
# AUTH MIDDLEWARE
# =========================================================

def super_admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get("role") != "super_admin":

            flash("Unauthorized access", "danger")
            return redirect("/auth/login")

        return f(*args, **kwargs)

    return wrapper


# =========================================================
# HELPERS
# =========================================================

def get_controlled_admin_ids():

    return [
        admin[0]
        for admin in db.session.query(User.id).filter(
            User.role == "admin",
            User.controller_id == session.get("user_id")
        ).all()
    ]


def get_controlled_user_ids():

    admin_ids = get_controlled_admin_ids()

    if not admin_ids:
        return []

    return [
        user[0]
        for user in db.session.query(User.id).filter(
            User.role == "user",
            User.controller_id.in_(admin_ids)
        ).all()
    ]


# =========================================================
# DASHBOARD
# =========================================================

@super_admin.route("/")
@super_admin_required
def dashboard_page():

    admin_ids = get_controlled_admin_ids()
    user_ids = get_controlled_user_ids()

    total_admins = len(admin_ids)

    total_users = User.query.filter(
        User.id.in_(user_ids)
    ).count()

    active_users = User.query.filter(
        User.id.in_(user_ids),
        User.status == "active"
    ).count()

    blocked_users = User.query.filter(
        User.id.in_(user_ids),
        User.status == "blocked"
    ).count()

    total_applications = WorkApplication.query.filter(
        WorkApplication.user_id.in_(user_ids)
    ).count()

    recent_users = User.query.filter(
        User.id.in_(user_ids)
    ).order_by(
        User.id.desc()
    ).limit(10).all()

    return render_template(
        "super_admin/dashboard.html",
        total_admins=total_admins,
        total_users=total_users,
        active_users=active_users,
        blocked_users=blocked_users,
        total_applications=total_applications,
        recent_users=recent_users,
        now=datetime.utcnow()
    )


# =========================================================
# ADMINS PAGE
# =========================================================

@super_admin.route("/admins")
@super_admin_required
def view_admins():

    page = request.args.get("page", 1, type=int)

    admins = User.query.filter(
        User.role == "admin",
        User.controller_id == session.get("user_id")
    ).order_by(
        User.id.desc()
    ).paginate(
        page=page,
        per_page=20
    )

    return render_template(
        "super_admin/admins.html",
        admins=admins
    )


# =========================================================
# USERS PAGE
# =========================================================

@super_admin.route("/users")
@super_admin_required
def super_admin_users():

    admin_ids = get_controlled_admin_ids() or []
    user_ids = get_controlled_user_ids() or []

    admin_filter = User.id.in_(admin_ids) if admin_ids else False
    user_filter = User.id.in_(user_ids) if user_ids else False

    page = request.args.get("page", 1, type=int)

    users = User.query.options(
    joinedload(User.profile)
    ).filter(
        User.is_deleted.is_(False),
        (
            (User.role == "admin") & admin_filter
        ) |
        (
            (User.role == "user") & user_filter
        )
    ).order_by(
        User.id.desc()
    ).paginate(
        page=page,
        per_page=20
    )

    return render_template(
        "super_admin/users.html",
        users=users,
        total=users.total,
        admin_count=len(admin_ids),
        user_count=len(user_ids)
    )


# =========================================================
# APPLICATIONS PAGE
# =========================================================

@super_admin.route("/applications")
@super_admin_required
def applications():

    try:

        page = max(
            request.args.get(
                "page",
                1,
                type=int
            ),
            1
        )

        user_ids = get_controlled_user_ids()

        if not user_ids:

            return render_template(
                "super_admin/applications.html",
                applications=None
            )

        applications = (
            WorkApplication.query
            .options(
                joinedload(
                    WorkApplication.user
                )
            )
            .filter(
                WorkApplication.user_id.in_(
                    user_ids
                ),
                WorkApplication.is_deleted.is_(False)
            )
            .order_by(
                WorkApplication.id.desc()
            )
            .paginate(
                page=page,
                per_page=20,
                error_out=False
            )
        )

        return render_template(
            "super_admin/applications.html",
            applications=applications
        )

    except Exception as e:

        current_app.logger.error(
            f"Applications page error: {e}"
        )

        flash(
            "Unable to load applications.",
            "danger"
        )

        return redirect(
            url_for(
                "super_admin.dashboard_page"
            )
        )

# =========================================================
# USER PROFILE PAGE
# =========================================================

@super_admin.route("/user/<int:user_id>")
@super_admin_required
def super_admin_user_profile(user_id):

    # ==========================================
    # AUTHORIZATION CHECK
    # ==========================================

    allowed_ids = (
        get_controlled_admin_ids() +
        get_controlled_user_ids()
    )

    if user_id not in allowed_ids:

        flash("Unauthorized access", "danger")
        return redirect(url_for("super_admin.super_admin_users"))

    # ==========================================
    # PAGINATION
    # ==========================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    # ==========================================
    # USER + PROFILE
    # ==========================================

    user = (
        User.query
        .options(
            joinedload(User.profile)
        )
        .filter(
            User.id == user_id,
            User.is_deleted.is_(False)
        )
        .first()
    )

    if not user:

        flash("User not found", "danger")
        return redirect(
            url_for("super_admin.super_admin_users")
        )

    profile = user.profile

    # ==========================================
    # WORKS PAGINATION
    # ==========================================

    works = (
        Work.query
        .filter(
            Work.user_id == user.id
        )
        .order_by(
            Work.id.desc()
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False
        )
    )

    # ==========================================
    # GALLERY PARSE
    # ==========================================

    gallery_images = []

    if profile and profile.gallery:

        try:
            gallery_images = json.loads(
                profile.gallery
            )

            if not isinstance(
                gallery_images,
                list
            ):
                gallery_images = []

        except (
            JSONDecodeError,
            TypeError
        ):
            gallery_images = []

    # ==========================================
    # ACTIVITY LOG
    # ==========================================

    log_activity(
        actor_id=session.get("user_id"),
        target_id=user.id,
        action="view_profile",
        role="super_admin"
    )

    # ==========================================
    # RESPONSE
    # ==========================================

    return render_template(
        "super_admin/user_profile.html",
        user=user,
        profile=profile,
        works=works,
        gallery_images=gallery_images
    )

# =========================================================
# UPDATE ADMIN STATUS
# =========================================================

@super_admin.route(
    "/admin/<int:admin_id>/status",
    methods=["POST"]
)
@super_admin_required
def update_admin_status(admin_id):

    action = request.form.get(
        "action",
        ""
    ).strip().lower()

    allowed_actions = {
        "approve": "active",
        "unblock": "active",
        "reject": "rejected",
        "block": "blocked"
    }

    if action not in allowed_actions:

        flash(
            "Invalid action",
            "danger"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    admin = (
        User.query
        .filter(
            User.id == admin_id,
            User.role == "admin",
            User.controller_id ==
            session.get("user_id"),
            User.is_deleted.is_(False)
        )
        .first()
    )

    if not admin:

        flash(
            "Admin not found",
            "danger"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    old_status = admin.status
    new_status = allowed_actions[action]

    # No-op update protection
    if old_status == new_status:

        flash(
            f"Admin is already {new_status}",
            "info"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    try:

        admin.status = new_status
        admin.updated_at = datetime.utcnow()

        db.session.commit()

        # Realtime notification
        socketio.emit(
            "notify",
            {
                "message":
                f"Your account status changed to {new_status}"
            },
            room=f"user_{admin.id}"
        )

        # Audit Log
        log_activity(
            actor_id=session.get("user_id"),
            target_id=admin.id,
            action=action,
            role="super_admin",
            meta={
                "old_status": old_status,
                "new_status": new_status
            }
        )

        flash(
            f"Admin {action} successful",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        current_app.logger.error(
            f"Admin status update failed: {e}"
        )

        flash(
            "Database error occurred",
            "danger"
        )

    return redirect(
        url_for(
            "super_admin.view_admins"
        )
    )

# =========================================================
# BULK ACTION
# =========================================================


@super_admin.route(
    "/admins/bulk",
    methods=["POST"]
)
@super_admin_required
def bulk_admin_action():

    ids = request.form.getlist("ids")
    action = request.form.get(
        "action",
        ""
    ).strip().lower()

    allowed_actions = {
        "approve": "active",
        "unblock": "active",
        "block": "blocked"
    }

    # ===============================
    # VALIDATION
    # ===============================

    if not ids:

        flash(
            "No admin selected",
            "danger"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    if action not in allowed_actions:

        flash(
            "Invalid action",
            "danger"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    try:

        ids = [
            int(i)
            for i in ids
        ]

    except ValueError:

        flash(
            "Invalid admin IDs",
            "danger"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    # ===============================
    # FETCH ADMINS
    # ===============================

    admins = (
        User.query
        .filter(
            User.id.in_(ids),
            User.role == "admin",
            User.controller_id ==
            session.get("user_id"),
            User.is_deleted.is_(False)
        )
        .all()
    )

    if not admins:

        flash(
            "No valid admins found",
            "warning"
        )
        return redirect(
            url_for(
                "super_admin.view_admins"
            )
        )

    updated_count = 0

    try:

        for admin in admins:

            old_status = admin.status
            new_status = allowed_actions[action]

            # Skip if already same status
            if old_status == new_status:
                continue

            admin.status = new_status
            admin.updated_at = datetime.utcnow()

            updated_count += 1

            # Audit Log
            log_activity(
                actor_id=session.get("user_id"),
                target_id=admin.id,
                action=f"bulk_{action}",
                role="super_admin",
                meta={
                    "old_status": old_status,
                    "new_status": new_status
                }
            )

        db.session.commit()

        # ===============================
        # SOCKET NOTIFICATIONS
        # ===============================

        for admin in admins:

            socketio.emit(
                "notify",
                {
                    "message":
                    f"Your account status changed to {admin.status}"
                },
                room=f"user_{admin.id}"
            )

        flash(
            f"{updated_count} admin(s) updated successfully",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        current_app.logger.error(
            f"Bulk admin update failed: {e}"
        )

        flash(
            "Database error occurred",
            "danger"
        )

    return redirect(
        url_for(
            "super_admin.view_admins"
        )
    )

# =========================================================
# LOGS PAGE
# =========================================================

@super_admin.route("/logs")
@super_admin_required
def get_logs():

    try:

        admin_ids = get_controlled_admin_ids()

        if not admin_ids:

            return render_template(
                "super_admin/logs.html",
                logs=None
            )

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
        ).strip()

        query = (
            ActivityLog.query
            .filter(
                ActivityLog.target_id.in_(admin_ids)
            )
        )

        # Optional Search
        if search:

            query = query.filter(
                ActivityLog.action.ilike(
                    f"%{search}%"
                )
            )

        logs = (
            query
            .order_by(
                ActivityLog.timestamp.desc()
            )
            .paginate(
                page=page,
                per_page=30,
                error_out=False
            )
        )

        return render_template(
            "super_admin/logs.html",
            logs=logs,
            search=search
        )

    except Exception as e:

        current_app.logger.error(
            f"Logs page error: {e}"
        )

        flash(
            "Unable to load logs",
            "danger"
        )

        return redirect(
            url_for(
                "super_admin.dashboard_page"
            )
        )

# =========================================================
# ANALYTICS PAGE
# =========================================================

@super_admin.route("/analytics")
@super_admin_required
def analytics():

    try:

        start = datetime.utcnow() - timedelta(days=30)

        admin_ids = get_controlled_admin_ids()
        user_ids = get_controlled_user_ids()

        total_admins = len(admin_ids)

        total_users = User.query.filter(
            User.id.in_(user_ids),
            User.is_deleted.is_(False)
        ).count()

        active_users = User.query.filter(
            User.id.in_(user_ids),
            User.status == "active",
            User.is_deleted.is_(False)
        ).count()

        blocked_users = User.query.filter(
            User.id.in_(user_ids),
            User.status == "blocked",
            User.is_deleted.is_(False)
        ).count()

        total_applications = WorkApplication.query.filter(
            WorkApplication.user_id.in_(user_ids),
            WorkApplication.is_deleted.is_(False)
        ).count()

        growth = db.session.query(
            func.date(User.created_at),
            func.count(User.id)
        ).filter(
            User.id.in_(user_ids),
            User.created_at >= start,
            User.is_deleted.is_(False)
        ).group_by(
            func.date(User.created_at)
        ).all()

        return render_template(
            "super_admin/analytics.html",
            total_admins=total_admins,
            total_users=total_users,
            active_users=active_users,
            blocked_users=blocked_users,
            total_applications=total_applications,
            growth=growth
        )

    except Exception as e:

        current_app.logger.error(
            f"Analytics Error: {str(e)}"
        )

        flash(
            "Something went wrong while loading analytics.",
            "danger"
        )

        return redirect(
            url_for(
                "super_admin.dashboard_page"
            )
        )
