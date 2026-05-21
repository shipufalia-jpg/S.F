from flask import Blueprint, render_template, session, redirect, request, jsonify
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta

from extensions import db, socketio

from models.user import User
from models.work_model import Work
from models.booking import Booking


owner = Blueprint('owner', __name__)


# =================================================
# 🔐 OWNER ONLY DECORATOR
# =================================================
def owner_only(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get("role") != "owner":
            return "Unauthorized", 403

        return f(*args, **kwargs)

    return wrapper


# =================================================
# 👤 APPROVE ADMIN / SUPER ADMIN
# =================================================
@owner.route('/owner/approve/<int:id>', methods=["POST"])
@owner_only
def approve_user(id):

    user = User.query.get(id)

    if not user:
        return "User not found"

    if user.role not in ["admin", "super_admin"]:
        return "No approval needed"

    user.status = "active"
    db.session.commit()

    return redirect('/owner/dashboard')


# =================================================
# 🔁 TRANSFER USER
# =================================================
@owner.route('/owner/transfer', methods=['POST'])
@owner_only
def transfer_user():

    user_id = int(request.form['user_id'])
    new_controller = int(request.form['new_controller'])

    if user_id == new_controller:
        return "Invalid operation"

    user = User.query.get(user_id)
    controller = User.query.get(new_controller)

    if not user or not controller:
        return "Invalid user"

    if controller.role not in ["admin", "super_admin"]:
        return "Invalid controller role"

    user.controller_id = controller.id

    db.session.commit()

    socketio.emit("notify", {
        "message": f"{user.name} transferred successfully 🔁"
    })

    return redirect('/owner/dashboard')


# =================================================
# 📋 ALL WORKS (FILTER SUPPORT)
# =================================================
@owner.route('/owner/works')
@owner_only
def all_works():

    status = request.args.get("status")

    query = Work.query.filter(
        Work.status != "deleted"
    )

    if status:
        query = query.filter_by(status=status)

    works = query.order_by(Work.id.desc()).all()

    return render_template("owner_works.html", works=works)


# =================================================
# ✅ APPROVE WORK
# =================================================
@owner.route('/owner/work/approve/<int:id>')
@owner_only
def approve_work(id):

    work = Work.query.get_or_404(id)

    work.status = "approved"

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# ❌ REJECT WORK
# =================================================
@owner.route('/owner/work/reject/<int:id>')
@owner_only
def reject_work(id):

    work = Work.query.get_or_404(id)

    work.status = "rejected"

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# ✏️ EDIT WORK (FIXED FOR WORK_MODEL)
# =================================================
@owner.route('/owner/work/edit/<int:id>', methods=['GET', 'POST'])
@owner_only
def edit_work(id):

    work = Work.query.get_or_404(id)

    if request.method == "POST":

        work.title = request.form['title']
        work.description = request.form['description']
        work.mobile = request.form['mobile']

        work.status = "pending"  # re-verify after edit

        db.session.commit()

        return redirect('/owner/works')

    return render_template("edit_work.html", work=work)


# =================================================
# 🗑 DELETE WORK (SOFT DELETE)
# =================================================
@owner.route('/owner/work/delete/<int:id>')
@owner_only
def delete_work(id):

    work = Work.query.get_or_404(id)

    work.status = "deleted"

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# 📊 OWNER ANALYTICS API
# =================================================
@owner.route('/owner/analytics')
@owner_only
def owner_analytics():

    days = request.args.get("days", 30, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    total_works = db.session.query(func.count(Work.id)).scalar()

    approved_works = db.session.query(func.count(Work.id)).filter(
        Work.status == "approved"
    ).scalar()

    pending_works = db.session.query(func.count(Work.id)).filter(
        Work.status == "pending"
    ).scalar()

    rejected_works = db.session.query(func.count(Work.id)).filter(
        Work.status == "rejected"
    ).scalar()

    deleted_works = db.session.query(func.count(Work.id)).filter(
        Work.status == "deleted"
    ).scalar()

    total_users = db.session.query(func.count(User.id)).filter(
        User.role == "user"
    ).scalar()

    active_users = db.session.query(func.count(User.id)).filter(
        User.role == "user",
        User.status == "active"
    ).scalar()

    blocked_users = total_users - active_users

    work_growth = db.session.query(
        func.date(Work.created_at),
        func.count(Work.id)
    ).filter(
        Work.created_at >= start_date
    ).group_by(func.date(Work.created_at)).all()

    user_growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.role == "user",
        User.created_at >= start_date
    ).group_by(func.date(User.created_at)).all()

    return jsonify({
        "success": True,
        "data": {
            "works": {
                "total": total_works,
                "approved": approved_works,
                "pending": pending_works,
                "rejected": rejected_works,
                "deleted": deleted_works
            },
            "users": {
                "total": total_users,
                "active": active_users,
                "blocked": blocked_users
            },
            "growth": {
                "works": [{"date": str(g[0]), "count": g[1]} for g in work_growth],
                "users": [{"date": str(g[0]), "count": g[1]} for g in user_growth]
            }
        }
    })


# =================================================
# 🏠 OWNER DASHBOARD (CLEAN + FIXED)
# =================================================
@owner.route('/owner/dashboard')
@owner_only
def owner_dashboard():

    total_users = User.query.filter_by(role="user").count()

    total_admins = User.query.filter(
        User.role.in_(["admin", "super_admin"])
    ).count()

    pending_admins = User.query.filter(
        User.role.in_(["admin", "super_admin"]),
        User.status == "pending"
    ).all()

    total_works = Work.query.filter(
        Work.status != "deleted"
    ).count()

    approved_works = Work.query.filter_by(status="approved").count()

    pending_works = Work.query.filter_by(status="pending").count()

    latest_users = User.query.order_by(User.id.desc()).all()

    latest_bookings = Booking.query.order_by(
        Booking.id.desc()
    ).limit(20).all()

    return render_template(
        "owner/dashboard.html",
        total_users=total_users,
        total_admins=total_admins,
        pending_admins=pending_admins,
        total_works=total_works,
        approved_works=approved_works,
        pending_works=pending_works,
        latest_users=latest_users,
        latest_bookings=latest_bookings
)
# =========================================
# WORKS PARTIAL LOAD (AJAX FILTER)
# PRODUCTION VERSION
# =========================================
@owner.route('/owner/works/partial')
@owner_only
def works_partial():

    # ================= FILTER =================
    status = request.args.get("status", type=str)
    search = request.args.get("search", type=str, default="").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 12

    # ================= BASE QUERY =================
    query = Work.query.filter(Work.status != "deleted")

    # ================= STATUS FILTER =================
    if status and status != "all":
        query = query.filter(Work.status == status)

    # ================= SEARCH FILTER =================
    if search:
        query = query.filter(
            Work.title.ilike(f"%{search}%")
        )

    # ================= PAGINATION =================
    works_paginated = query.order_by(
        Work.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # ================= RESPONSE =================
    return render_template(
        "partials/owner_works_partial.html",
        works=works_paginated.items,
        pagination=works_paginated,
        current_page=page,
        status=status,
        search=search
    )
    