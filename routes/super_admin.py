from flask import Blueprint, session, jsonify, request, render_template
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from models.user import User
from models.work_model import Work
from models.work_application import WorkApplication
from models.booking import Booking
from models.activity_log import ActivityLog
from extensions import db
from extensions import socketio
from services.logger import log_activity
from utils.decorators import login_required, admin_required

super_admin = Blueprint('super_admin', __name__, url_prefix="/super")

# ================= RESPONSE =================

def success(data=None, message="OK"):
    return jsonify({"success": True, "message": message, "data": data}), 200

def error(msg="Error", code=400):
    return jsonify({"success": False, "message": msg}), code


# ================= AUTH =================

def super_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != "super_admin":
            return error("Unauthorized", 403)
        return f(*args, **kwargs)
    return wrapper


# ================= DASHBOARD =================

@super_admin.route('/')
@super_admin_required
def dashboard_page():
    return render_template("super_admin/dashboard.html",
        user_id=session.get("user_id"),
        now=datetime.utcnow()
    )


# ================= ADMIN LIST (PAGINATION) =================

@super_admin.route('/admins')
@super_admin_required
def view_admins():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    query = User.query.filter_by(
        role="admin",
        controller_id=session['user_id']
    )

    admins = query.paginate(page=page, per_page=limit)

    return success({
        "admins": [{
            "id": a.id,
            "name": a.username,
            "status": a.status
        } for a in admins.items],
        "pagination": {
            "total": admins.total,
            "pages": admins.pages,
            "current": admins.page
        }
    })


# ================= UPDATE ADMIN =================

@super_admin.route('/admin/<int:id>/status', methods=["POST"])
@super_admin_required
def update_admin_status(id):

    user = User.query.get_or_404(id)

    if user.controller_id != session['user_id'] or user.role != "admin":
        return error("Forbidden", 403)

    data = request.get_json(silent=True) or {}
    action = data.get("action")

    if action not in ["approve", "block", "unblock"]:
        return error("Invalid action")

    old_status = user.status
    user.status = "blocked" if action == "block" else "active"

    db.session.commit()

    # 🔔 notification
    socketio.emit('notify',
        {"message": f"Admin {action}"},
        room=f"user_{user.id}"
    )

    # 🧠 logging
    log_activity(
        actor_id=session['user_id'],
        target_id=user.id,
        action=action,
        role="super_admin",
        meta={
            "old_status": old_status,
            "new_status": user.status
        }
    )

    return success(message=f"Admin {action} done")


# ================= BULK ACTION =================

@super_admin.route('/admins/bulk', methods=["POST"])
@super_admin_required
def bulk_admin_action():

    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    action = data.get("action")

    if not ids or action not in ["approve", "block", "unblock"]:
        return error("Invalid request")

    admins = User.query.filter(
        User.id.in_(ids),
        User.role == "admin",
        User.controller_id == session['user_id']
    ).all()

    for admin in admins:
        admin.status = "blocked" if action == "block" else "active"

        socketio.emit('notify',
            {"message": f"Admin {action}"},
            room=f"user_{admin.id}"
        )

    db.session.commit()

    return success(message=f"Bulk {action} done")


# ================= LOGS (ADVANCED FILTER) =================

@super_admin.route('/logs')
@super_admin_required
def get_logs():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    action = request.args.get("action")
    role = request.args.get("role")
    start = request.args.get("start")
    end = request.args.get("end")

    query = ActivityLog.query

    if action:
        query = query.filter(ActivityLog.action == action)

    if role:
        query = query.filter(ActivityLog.role == role)

    if start and end:
        try:
            start = datetime.strptime(start, "%Y-%m-%d")
            end = datetime.strptime(end, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59)

            query = query.filter(ActivityLog.timestamp.between(start, end))
        except:
            return error("Invalid date format")

    logs = query.order_by(ActivityLog.timestamp.desc())\
                .paginate(page=page, per_page=limit)

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


# ================= ANALYTICS (OPTIMIZED) =================

@super_admin.route('/analytics')
@super_admin_required
def analytics():

    start = datetime.utcnow() - timedelta(days=30)

    total_users = db.session.query(func.count(User.id))\
        .filter(User.role == "user").scalar()

    active_users = db.session.query(func.count(User.id))\
        .filter(User.role == "user", User.status == "active").scalar()

    total_admins = db.session.query(func.count(User.id))\
        .filter(User.role == "admin").scalar()

    # 📊 growth (limited)
    growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(User.created_at >= start)\
     .group_by(func.date(User.created_at)).all()

    # 📈 last 7 days growth %
    last_7 = datetime.utcnow() - timedelta(days=7)
    new_users = db.session.query(func.count(User.id))\
        .filter(User.created_at >= last_7).scalar()

    growth_percent = round((new_users / total_users * 100), 2) if total_users else 0

    return success({
        "users": {
            "total": total_users,
            "active": active_users,
            "blocked": total_users - active_users,
            "growth_percent": growth_percent
        },
        "admins": {
            "total": total_admins
        },
        "growth": [
            {"date": str(g[0]), "count": g[1]} for g in growth
        ]
    })
