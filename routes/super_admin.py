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

    user_ids = get_controlled_user_ids()

    apps = WorkApplication.query.filter(
        WorkApplication.user_id.in_(user_ids),
        WorkApplication.is_deleted.is_(False)
    ).order_by(
        WorkApplication.id.desc()
    ).all()

    return render_template(
        "super_admin/applications.html",
        applications=apps
    )


# =========================================================
# USER PROFILE PAGE
# =========================================================

@super_admin.route("/user/<int:user_id>")
@super_admin_required
def super_admin_user_profile(user_id):

    user = User.query.options(
        joinedload(User.profile)
    ).filter_by(
        id=user_id,
        is_deleted=False
    ).first()

    if not user:

        flash("User not found", "danger")
        return redirect("/super/users")

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    works = Work.query.filter_by(
        user_id=user.id
    ).all()

    gallery_images = []

    if profile and profile.gallery:

        try:
            gallery_images = json.loads(profile.gallery)

        except Exception:
            gallery_images = []

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

@super_admin.route("/admin/<int:id>/status/<string:action>")
@super_admin_required
def update_admin_status(id, action):

    admin = User.query.filter(
        User.id == id,
        User.role == "admin",
        User.controller_id == session.get("user_id")
    ).first_or_404()

    allowed_actions = [
        "approve",
        "reject",
        "block",
        "unblock"
    ]

    if action not in allowed_actions:

        flash("Invalid action", "danger")
        return redirect("/super/admins")

    old_status = admin.status

    if action in ["approve", "unblock"]:
        admin.status = "active"

    elif action == "reject":
        admin.status = "rejected"

    elif action == "block":
        admin.status = "blocked"

    db.session.commit()

    # SOCKET NOTIFICATION
    socketio.emit(
        "notify",
        {
            "message": f"Your account status changed to {admin.status}"
        },
        room=f"user_{admin.id}"
    )

    # ACTIVITY LOG
    log_activity(
        actor_id=session.get("user_id"),
        target_id=admin.id,
        action=action,
        role="super_admin",
        meta={
            "old_status": old_status,
            "new_status": admin.status
        }
    )

    flash(f"Admin {action} successful", "success")

    return redirect("/super/admins")


# =========================================================
# BULK ACTION
# =========================================================

@super_admin.route("/admins/bulk", methods=["POST"])
@super_admin_required
def bulk_admin_action():

    ids = request.form.getlist("ids")
    action = request.form.get("action")

    if not ids:

        flash("No admin selected", "danger")
        return redirect("/super/admins")

    if action not in ["approve", "block", "unblock"]:

        flash("Invalid action", "danger")
        return redirect("/super/admins")

    admins = User.query.filter(
        User.id.in_(ids),
        User.role == "admin",
        User.controller_id == session.get("user_id")
    ).all()

    for admin in admins:

        if action == "block":
            admin.status = "blocked"

        else:
            admin.status = "active"

        socketio.emit(
            "notify",
            {
                "message": f"Admin status updated: {admin.status}"
            },
            room=f"user_{admin.id}"
        )

    db.session.commit()

    flash(f"Bulk {action} successful", "success")

    return redirect("/super/admins")


# =========================================================
# LOGS PAGE
# =========================================================

@super_admin.route("/logs")
@super_admin_required
def get_logs():

    admin_ids = get_controlled_admin_ids()

    page = request.args.get("page", 1, type=int)

    logs = ActivityLog.query.filter(
        ActivityLog.target_id.in_(admin_ids)
    ).order_by(
        ActivityLog.timestamp.desc()
    ).paginate(
        page=page,
        per_page=30
    )

    return render_template(
        "super_admin/logs.html",
        logs=logs
    )


# =========================================================
# ANALYTICS PAGE
# =========================================================

@super_admin.route("/analytics")
@super_admin_required
def analytics():

    start = datetime.utcnow() - timedelta(days=30)

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

    growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.id.in_(user_ids),
        User.created_at >= start
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

@super.route("/dashboard")
def dashboard():

    sid = session.get("user_id")

    admins = User.query.filter_by(role="admin").all()

    chambers = Chamber.query.filter_by(controller_admin_id=sid).all()

    return render_template(
        "super/dashboard.html",
        admins=admins,
        chambers=chambers
    )
