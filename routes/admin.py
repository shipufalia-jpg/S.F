from flask import Blueprint, render_template, session, jsonify, request
from functools import wraps
from models.user import User
from models.booking import Booking
from models.work_model import Work
from models.work_application import WorkApplication
from extensions import db
from sqlalchemy.orm import load_only
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("limit", 20, type=int)
    search = request.args.get("search", "")

    query = User.query.filter_by(controller_id=user_id)\
        .options(load_only(User.id, User.name, User.status))

    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))

    users = query.paginate(page=page, per_page=per_page)

    return success({
        "users": [{
            "id": u.id,
            "name": u.name,
            "status": u.status
        } for u in users.items],
        "pagination": {
            "total": users.total,
            "pages": users.pages,
            "current": users.page
        }
    })


# ================= USER STATUS =================

@admin_bp.route("/user/<int:id>/status", methods=["POST"])
@admin_required
def update_user_status(id):

    user = User.query.filter_by(
    id=id,
    controller_id=session.get("user_id")
).first_or_404()

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["active", "blocked"]:
        return error("Invalid status")

    user.status = status
    db.session.commit()

    return success(message=f"User {status}")


# ================= BULK ACTION =================

@admin_bp.route("/users/bulk", methods=["POST"])
@admin_required
def bulk_users():

    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    action = data.get("action")

    if action not in ["block", "unblock"]:
        return error("Invalid action")

    users = User.query.filter(
        User.id.in_(ids),
        User.controller_id == session.get("user_id")
    ).all()

    for u in users:
        u.status = "blocked" if action == "block" else "active"

    db.session.commit()

    return success(message="Bulk action completed")


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
    return render_template("admin/users.html")


# ================= USERS API (JSON) =================
@admin_bp.route("/api/users")
@admin_required
def users_api():

    user_id = session.get("user_id")

    users = User.query.filter_by(controller_id=user_id).all()

    return success({
        "users": [{
            "id": u.id,
            "name": u.name,
            "status": u.status
        } for u in users]
    })

# ================= USER DETAILS (POPUP) =================
@admin_bp.route("/user/<int:user_id>")
@admin_required
def get_user(user_id):

    admin_id = session.get("user_id")

    user = User.query.filter_by(
        id=user_id,
        controller_id=admin_id,
        is_deleted=False
    ).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,

            "phone": user.phone,
            "email": user.email,

            "skill": getattr(user, "skill", None),
            "area": getattr(user, "area", None),

            "profile_img": user.profile_img or "/static/default.png",

            "role": user.role,
            "status": user.status,

            "is_online": user.is_online,
            "last_seen": user.last_seen.isoformat() if user.last_seen else None,

            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    })
    
