from flask import Blueprint, session, jsonify, request, render_template, flash, redirect
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
import json

from sqlalchemy.orm import joinedload

from models.profile import Profile
from models.chat import Chat
from models.user import User
from models.work_application import WorkApplication
from models.activity_log import ActivityLog

from extensions import db, socketio
from services.logger import log_activity

super_admin = Blueprint(
    'super_admin',
    __name__,
    url_prefix="/super"
)



def super_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get("role") != "super_admin":
            flash("Unauthorized access", "danger")
            return redirect("/auth/login")

        return f(*args, **kwargs)

    return wrapper


# =========================================================
# HELPERS (FIXED)
# =========================================================

def get_controlled_admin_ids():
    return [a[0] for a in db.session.query(User.id).filter(
        User.role == "admin",
        User.controller_id == session.get("user_id")
    ).all()]


def get_controlled_user_ids():

    admin_ids = get_controlled_admin_ids()

    if not admin_ids:
        return []

    return [u[0] for u in db.session.query(User.id).filter(
        User.role == "user",
        User.controller_id.in_(admin_ids)
    ).all()]


# =========================================================
# DASHBOARD
# =========================================================

@super_admin.route('/')
@super_admin_required
def dashboard_page():

    total_users = User.query.count()
    total_admins = User.query.filter_by(role="admin").count()
    active_users = User.query.filter_by(status="active").count()
    blocked_users = User.query.filter_by(status="blocked").count()

    return render_template(
        "super_admin/dashboard.html",
        total_users=total_users,
        total_admins=total_admins,
        active_users=active_users,
        blocked_users=blocked_users
    )


# =========================================================
# ADMINS
# =========================================================

@super_admin.route('/admins')
@super_admin_required
def view_admins():

    admins = User.query.filter_by(role="admin").order_by(User.id.desc()).all()

    return render_template(
        "super_admin/admins.html",
        admins=admins
    )


# =========================================================
# USERS
# =========================================================

@super_admin.route("/users")
@super_admin_required
def super_admin_users():

    admin_ids = get_controlled_admin_ids() or []
    user_ids = get_controlled_user_ids() or []

    # নিরাপদভাবে empty IN() crash prevent
    admin_filter = User.id.in_(admin_ids) if admin_ids else False
    user_filter = User.id.in_(user_ids) if user_ids else False

    users = User.query.filter(
        User.is_deleted.is_(False),
        (
            (User.role == "admin") & admin_filter
        ) |
        (
            (User.role == "user") & user_filter
        )
    ).order_by(User.id.desc()).all()

    return render_template(
        "super_admin/users.html",
        users=users,
        total=len(users),
        admin_count=len(admin_ids),
        user_count=len(user_ids)
    )


# =========================================================
# APPLICATIONS
# =========================================================

@super_admin.route('/applications')
@super_admin_required
def applications():

    user_ids = get_controlled_user_ids()

    apps = WorkApplication.query.filter(
        WorkApplication.user_id.in_(user_ids),
        WorkApplication.is_deleted == False
    ).order_by(WorkApplication.id.desc()).all()

    return render_template(
        "owner_applications.html",
        applications=apps
    )


# =========================================================
# ADMIN STATUS UPDATE
# =========================================================

@super_admin.route('/admin/<int:id>/status', methods=["POST"])
@super_admin_required
def update_admin_status(id):

    admin = User.query.filter(
        User.id == id,
        User.role == "admin",
        User.controller_id == session.get("user_id")
    ).first_or_404()

    data = request.get_json(silent=True) or {}
    action = data.get("action")

    allowed = ["approve", "reject", "block", "unblock"]

    if action not in allowed:
        return error("Invalid action")

    old_status = admin.status

    if action in ["approve", "unblock"]:
        admin.status = "active"
    elif action == "reject":
        admin.status = "rejected"
    elif action == "block":
        admin.status = "blocked"

    db.session.commit()

    socketio.emit(
        "notify",
        {"message": f"Your account status: {admin.status}"},
        room=f"user_{admin.id}"
    )

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

    return success(message=f"Admin {action} successful")


# =========================================================
# BULK ACTION
# =========================================================

@super_admin.route('/admins/bulk', methods=["POST"])
@super_admin_required
def bulk_admin_action():

    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    action = data.get("action")

    if not ids:
        return error("No admin selected")

    if action not in ["approve", "block", "unblock"]:
        return error("Invalid action")

    admins = User.query.filter(
        User.id.in_(ids),
        User.role == "admin",
        User.controller_id == session.get("user_id")
    ).all()

    for admin in admins:

        admin.status = "blocked" if action == "block" else "active"

        socketio.emit(
            "notify",
            {"message": f"Admin {action}"},
            room=f"user_{admin.id}"
        )

    db.session.commit()

    return success(message=f"Bulk {action} successful")


# =========================================================
# USER PROFILE
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
        return redirect("/super")

    profile = Profile.query.filter_by(user_id=user.id).first()
    works = Work.query.filter_by(user_id=user.id).all()

    gallery_images = []
    if profile and profile.gallery:
        try:
            gallery_images = json.loads(profile.gallery)
        except:
            gallery_images = []

    return render_template(
        "super_admin/user_profile.html",
        user=user,
        profile=profile,
        works=works,
        gallery_images=gallery_images
    )


# =========================================================
# LOGS (FIXED)
# =========================================================

@super_admin.route('/logs')
@super_admin_required
def get_logs():

    admin_ids = get_controlled_admin_ids()

    logs = ActivityLog.query.filter(
        ActivityLog.target_id.in_(admin_ids)
    ).order_by(ActivityLog.timestamp.desc()).all()

    return render_template(
        "super_admin/logs.html",
        logs=logs
    )

# =========================================================
# ANALYTICS
# =========================================================

@super_admin.route('/analytics')
@super_admin_required
def analytics():

    start = datetime.utcnow() - timedelta(days=30)

    admin_ids = get_controlled_admin_ids()
    user_ids = get_controlled_user_ids()

    data = {
        "total_admins": len(admin_ids),
        "total_users": len(user_ids),
        "active_users": User.query.filter(User.id.in_(user_ids), User.status=="active").count(),
        "blocked_users": User.query.filter(User.id.in_(user_ids), User.status=="blocked").count(),
        "total_applications": WorkApplication.query.filter(WorkApplication.user_id.in_(user_ids)).count()
    }

    growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.id.in_(user_ids),
        User.created_at >= start
    ).group_by(func.date(User.created_at)).all()

    return render_template(
        "super_admin/analytics.html",
        data=data,
        growth=growth
    )
