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

    # ================= ADMIN =================

    admin_id = session.get("user_id")

    if not admin_id:
        flash("Login required", "danger")
        return redirect("/auth/login")

    # ================= USER =================

    user = User.query.options(
        joinedload(User.profile)
    ).filter_by(
        id=user_id,
        controller_id=admin_id,
        is_deleted=False
    ).first()

    if not user:
        flash("User not found", "danger")
        return redirect("/admin/dashboard")

    # ================= PROFILE =================

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    # ================= WORKS =================

    works = Work.query.filter_by(
        user_id=user.id
    ).order_by(
        Work.id.desc()
    ).all()

    # ================= WORK IMAGES =================

    work_images = WorkImage.query.join(
        Work,
        Work.id == WorkImage.work_id
    ).filter(
        Work.user_id == user.id
    ).all()

    # ================= USER GALLERY =================

    galleries = Gallery.query.filter_by(
        user_id=user.id
    ).order_by(
        Gallery.id.desc()
    ).all()

    # ================= COUNTS =================

    total_works = len(works)

    total_gallery = len(galleries)

    total_work_images = len(work_images)

    total_applications = WorkApplication.query.filter_by(
        user_id=user.id
    ).count()

    total_chats = Chat.query.filter(
        (Chat.sender_id == user.id) |
        (Chat.receiver_id == user.id)
    ).count()

    # ================= ONLINE STATUS =================

    online_status = (
        "Online"
        if user.is_online
        else "Offline"
    )

    # ================= LAST SEEN =================

    last_seen = (
        user.last_seen.strftime("%d %b %Y %I:%M %p")
        if user.last_seen
        else None
    )

    # ================= JOIN DATE =================

    joined_date = (
        user.created_at.strftime("%d %b %Y")
        if user.created_at
        else None
    )

    # ================= PROFILE IMAGE =================

    profile_image = (
        user.profile_img
        if user.profile_img
        else "/static/default.png"
    )

    # ================= RETURN =================

    return render_template(

        "admin/user_profile.html",

        user=user,
        profile=profile,

        works=works,
        work_images=work_images,

        galleries=galleries,

        total_works=total_works,
        total_gallery=total_gallery,
        total_work_images=total_work_images,

        total_applications=total_applications,
        total_chats=total_chats,

        online_status=online_status,
        last_seen=last_seen,
        joined_date=joined_date,

        profile_image=profile_image
    )
