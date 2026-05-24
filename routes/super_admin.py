from flask import Blueprint, session, jsonify, request, render_template
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func

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

# =========================================================
# RESPONSE
# =========================================================

def success(data=None, message="OK"):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), 200


def error(msg="Error", code=400):
    return jsonify({
        "success": False,
        "message": msg
    }), code


# =========================================================
# AUTH
# =========================================================

def super_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get("role") != "super_admin":
            return error("Unauthorized", 403)

        return f(*args, **kwargs)

    return wrapper


# =========================================================
# HELPERS
# =========================================================

def get_controlled_admin_ids():

    admin_ids = db.session.query(User.id).filter(
        User.role == "admin",
        User.controller_id == session["user_id"]
    ).all()

    return [a[0] for a in admin_ids]


def get_controlled_user_ids():

    admin_ids = get_controlled_admin_ids()

    if not admin_ids:
        return []

    user_ids = db.session.query(User.id).filter(
        User.role == "user",
        User.controller_id.in_(admin_ids)
    ).all()

    return [u[0] for u in user_ids]


# =========================================================
# DASHBOARD
# =========================================================

@super_admin.route('/')
@super_admin_required
def dashboard_page():

    return render_template(
        "super_admin/dashboard.html",
        user_id=session.get("user_id"),
        now=datetime.utcnow()
    )


# =========================================================
# ADMINS LIST
# =========================================================

@super_admin.route('/admins')
@super_admin_required
def view_admins():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    query = User.query.filter(
        User.role == "admin",
        User.controller_id == session["user_id"]
    )

    admins = query.order_by(
        User.id.desc()
    ).paginate(page=page, per_page=limit)

    return success({
        "admins": [{
            "id": a.id,
            "name": a.name,
            "phone": a.phone,
            "status": a.status
        } for a in admins.items],

        "pagination": {
            "total": admins.total,
            "pages": admins.pages,
            "current": admins.page
        }
    })


# =========================================================
# USERS UNDER CONTROLLED ADMINS
# =========================================================

@super_admin.route('/users')
@super_admin_required
def controlled_users():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    admin_ids = get_controlled_admin_ids()

    users = User.query.filter(
        User.role == "user",
        User.controller_id.in_(admin_ids)
    ).order_by(
        User.id.desc()
    ).paginate(page=page, per_page=limit)

    return success({

        "users": [{

            "id": u.id,
            "name": u.name,
            "phone": u.phone,
            "email": getattr(u, "email", ""),
            "status": u.status,
            "controller_id": u.controller_id,

            "profile_image":
                u.profile.image
                if hasattr(u, "profile") and u.profile
                and getattr(u.profile, "image", None)
                else "https://i.pravatar.cc/150?img=12",

            "address":
                u.profile.address
                if hasattr(u, "profile") and u.profile
                and getattr(u.profile, "address", None)
                else "Not Added",

            "bio":
                u.profile.bio
                if hasattr(u, "profile") and u.profile
                and getattr(u.profile, "bio", None)
                else "No bio",

            "created_at":
                u.created_at.strftime("%d %b %Y")
                if u.created_at
                else "N/A"

        } for u in users.items],

        "pagination": {
            "total": users.total,
            "pages": users.pages,
            "current": users.page
        }

    })


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
    ).order_by(
        WorkApplication.id.desc()
    ).all()

    return render_template(
        "super_admin/applications.html",
        applications=apps
    )


# =========================================================
# APPROVE ADMIN
# =========================================================

@super_admin.route('/admin/<int:id>/status', methods=["POST"])
@super_admin_required
def update_admin_status(id):

    admin = User.query.filter(
        User.id == id,
        User.role == "admin",
        User.controller_id == session["user_id"]
    ).first_or_404()

    data = request.get_json(silent=True) or {}

    action = data.get("action")

    if action not in ["approve", "block", "unblock"]:
        return error("Invalid action")

    old_status = admin.status

    if action == "block":
        admin.status = "blocked"
    else:
        admin.status = "active"

    db.session.commit()

    # =====================================================
    # SOCKET NOTIFICATION
    # =====================================================

    socketio.emit(
        "notify",
        {"message": f"Admin {action}"},
        room=f"user_{admin.id}"
    )

    # =====================================================
    # LOG
    # =====================================================

    log_activity(
        actor_id=session["user_id"],
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
# BULK ADMIN ACTION
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
        User.controller_id == session["user_id"]
    ).all()

    for admin in admins:

        if action == "block":
            admin.status = "blocked"
        else:
            admin.status = "active"

        socketio.emit(
            "notify",
            {"message": f"Admin {action}"},
            room=f"user_{admin.id}"
        )

    db.session.commit()

    return success(message=f"Bulk {action} successful")


# =========================================================
# LOGS
# =========================================================

@super_admin.route('/logs')
@super_admin_required
def get_logs():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    controlled_admin_ids = get_controlled_admin_ids()

    query = ActivityLog.query.filter(
        ActivityLog.target_id.in_(controlled_admin_ids)
    )

    logs = query.order_by(
        ActivityLog.timestamp.desc()
    ).paginate(page=page, per_page=limit)

    return success({
        "logs": [{
            "id": l.id,
            "actor": l.actor_id,
            "target": l.target_id,
            "action": l.action,
            "role": l.role,
            "time": l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "meta": l.meta
        } for l in logs.items],

        "pagination": {
            "total": logs.total,
            "pages": logs.pages,
            "current": logs.page
        }
    })


# =========================================================
# ANALYTICS
# =========================================================

@super_admin.route('/analytics')
@super_admin_required
def analytics():

    start = datetime.utcnow() - timedelta(days=30)

    admin_ids = get_controlled_admin_ids()

    user_ids = get_controlled_user_ids()

    # =====================================================
    # COUNTS
    # =====================================================

    total_admins = len(admin_ids)

    total_users = db.session.query(
        func.count(User.id)
    ).filter(
        User.id.in_(user_ids)
    ).scalar()

    active_users = db.session.query(
        func.count(User.id)
    ).filter(
        User.id.in_(user_ids),
        User.status == "active"
    ).scalar()

    blocked_users = db.session.query(
        func.count(User.id)
    ).filter(
        User.id.in_(user_ids),
        User.status == "blocked"
    ).scalar()

    total_applications = db.session.query(
        func.count(WorkApplication.id)
    ).filter(
        WorkApplication.user_id.in_(user_ids)
    ).scalar()

    # =====================================================
    # USER GROWTH
    # =====================================================

    growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.id.in_(user_ids),
        User.created_at >= start
    ).group_by(
        func.date(User.created_at)
    ).all()

    return success({

        "admins": {
            "total": total_admins
        },

        "users": {
            "total": total_users,
            "active": active_users,
            "blocked": blocked_users
        },

        "applications": {
            "total": total_applications
        },

        "growth": [
            {
                "date": str(g[0]),
                "count": g[1]
            }
            for g in growth
        ]
    })
