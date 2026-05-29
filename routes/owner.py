from flask import (
    render_template,
    redirect,
    request,
    session,
    url_for,
    flash
)
from flask import Blueprint, render_template, session, redirect, request, jsonify
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta

from extensions import db, socketio
from models.withdraw import WithdrawRequest
from models.user import User
from models.work_model import Work
from models.booking import Booking
from models.work_application import WorkApplication


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
# 📋 ALL WORKS
# =================================================
@owner.route('/owner/works')
@owner_only
def all_works():

    # ================= GET FILTER =================
    status = request.args.get("status", "").strip()

    # ================= BASE QUERY =================
    query = Work.query.filter(
        Work.is_deleted == False
    )

    # ================= STATUS FILTER =================
    if status and status != "all":

        query = query.filter(
            Work.status == status
        )

    # ================= LATEST FIRST =================
    works = query.order_by(
        Work.id.desc()
    ).all()

    # ================= RENDER =================
    return render_template(
        "owner_works.html",
        works=works,
        current_status=status
    )


# =================================================
# ✅ APPROVE WORK
# =================================================
@owner.route('/owner/work/approve/<int:id>')
@owner_only
def approve_work(id):

    work = Work.query.get_or_404(id)

    # ================= ALREADY APPROVED =================
    if work.status == "approved":

        flash("Work already approved", "info")

        return redirect('/owner/dashboard')

    # ================= APPROVE =================
    work.status = "approved"

    work.is_active = True

    work.is_deleted = False

    work.approved_by = session.get("user_id")

    work.updated_at = datetime.utcnow()

    db.session.commit()

    # ================= REALTIME SOCKET =================
    socketio.emit("work_update", {

        "type": "approved",

        "work_id": work.id,

        "title": work.title,

        "message": f"{work.title} approved successfully"

    })

    flash("Work approved successfully", "success")

    return redirect('/owner/dashboard')


# =================================================
# ❌ REJECT WORK
# =================================================
@owner.route('/owner/work/reject/<int:id>')
@owner_only
def reject_work(id):

    work = Work.query.get_or_404(id)

    # ================= ALREADY REJECTED =================
    if work.status == "rejected":

        flash("Work already rejected", "info")

        return redirect('/owner/dashboard')

    # ================= REJECT =================
    work.status = "rejected"

    work.is_active = False

    work.rejected_by = session.get("user_id")

    work.updated_at = datetime.utcnow()

    db.session.commit()
    send_notification(

    user_id=user.id,

    title="Account Rejected",

    message="Sorry, your account has been rejected.",

    type="reject",

    icon="x-circle",

    priority="high"
    )

    # ================= SOCKET =================
    socketio.emit("work_update", {

        "type": "rejected",

        "work_id": work.id,

        "title": work.title,

        "message": f"{work.title} rejected"

    })

    flash("Work rejected successfully", "warning")

    return redirect('/owner/dashboard')


# =================================================
# ✏️ EDIT WORK
# =================================================
@owner.route('/owner/work/edit/<int:id>', methods=['GET', 'POST'])
@owner_only
def edit_work(id):

    work = Work.query.get_or_404(id)

    # ================= UPDATE =================
    if request.method == "POST":

        title = request.form.get('title')
        description = request.form.get('description')
        mobile = request.form.get('mobile')

        # ================= VALIDATION =================
        if not title or not description or not mobile:

            flash("All fields required", "danger")

            return redirect(
                url_for(
                    'owner.edit_work',
                    id=id
                )
            )

        # ================= SAVE =================
        work.title = title

        work.description = description

        work.mobile = mobile

        # RE-VERIFY AFTER EDIT
        work.status = "pending"

        work.is_active = False

        work.edited_by = session.get("user_id")

        work.edit_count += 1

        work.updated_at = datetime.utcnow()

        db.session.commit()

        # ================= SOCKET =================
        socketio.emit("work_update", {

            "type": "edited",

            "work_id": work.id,

            "title": work.title,

            "message": f"{work.title} edited"

        })

        flash(
            "Work updated and moved to pending review",
            "success"
        )

        return redirect('/owner/dashboard')

    return render_template(
        "edit_work.html",
        work=work
    )


# =================================================
# 🗑 DELETE WORK (SOFT DELETE)
# =================================================
@owner.route('/owner/work/delete/<int:id>')
@owner_only
def delete_work(id):

    work = Work.query.get_or_404(id)

    # ================= ALREADY DELETED =================
    if work.is_deleted:

        flash("Work already deleted", "info")

        return redirect('/owner/dashboard')

    # ================= DELETE =================
    work.status = "deleted"

    work.is_deleted = True

    work.is_active = False

    work.updated_at = datetime.utcnow()

    db.session.commit()

    # ================= SOCKET =================
    socketio.emit("work_update", {

        "type": "deleted",

        "work_id": work.id,

        "title": work.title,

        "message": f"{work.title} deleted"

    })

    flash("Work deleted successfully", "danger")

    return redirect('/owner/dashboard')


# =================================================
# ♻️ RESTORE DELETED WORK
# =================================================
@owner.route('/owner/work/restore/<int:id>')
@owner_only
def restore_work(id):

    work = Work.query.get_or_404(id)

    # ================= RESTORE =================
    work.status = "pending"

    work.is_deleted = False

    work.is_active = False

    work.updated_at = datetime.utcnow()

    db.session.commit()

    flash(
        "Work restored and pending approval",
        "success"
    )

    return redirect('/owner/dashboard')

# =================================================
# 👤 BLOCK USER
# =================================================
@owner.route('/owner/user/block/<int:id>')
@owner_only
def block_user(id):

    user = User.query.get_or_404(id)

    # OWNER নিজেকে block করতে পারবে না
    if user.role == "owner":
        flash("Owner account cannot be blocked", "danger")
        return redirect('/owner/dashboard')

    user.status = "blocked"

    db.session.commit()
    send_notification(

    user_id=user.id,

    title="Account Blocked",

    message="Your account has been blocked by admin.",

    type="block",

    icon="ban",

    priority="high"
        )

    socketio.emit("notify", {
        "type": "warning",
        "message": f"{user.name} has been blocked 🚫"
    })

    flash("User blocked successfully", "success")

    return redirect('/owner/dashboard')


# =================================================
# 👤 UNBLOCK USER
# =================================================
@owner.route('/owner/user/unblock/<int:id>')
@owner_only
def unblock_user(id):

    user = User.query.get_or_404(id)

    user.status = "active"

    db.session.commit()

    socketio.emit("notify", {
        "type": "success",
        "message": f"{user.name} has been unblocked ✅"
    })

    flash("User unblocked successfully", "success")

    return redirect('/owner/dashboard')


# =================================================
# 🗑 SOFT DELETE USER
# =================================================
@owner.route('/owner/user/delete/<int:id>')
@owner_only
def delete_user(id):

    user = User.query.get_or_404(id)

    # OWNER SAFE
    if user.role == "owner":
        flash("Owner account cannot be deleted", "danger")
        return redirect('/owner/dashboard')

    # SOFT DELETE
    user.status = "deleted"

    # OPTIONAL
    if hasattr(user, "is_deleted"):
        user.is_deleted = True

    db.session.commit()

    socketio.emit("notify", {
        "type": "danger",
        "message": f"{user.name} deleted successfully 🗑"
    })

    flash("User deleted successfully", "success")

    return redirect('/owner/dashboard')


# =================================================
# 👁 ADVANCED USER PROFILE VIEW
# =================================================
@owner.route('/owner/user/<int:id>')
@owner_only
def user_profile(id):

    user = User.query.get_or_404(id)

    # USER WORKS
    works = Work.query.filter_by(
        user_id=user.id
    ).order_by(
        Work.id.desc()
    ).all()

    # TOTAL COUNTS
    total_works = Work.query.filter_by(user_id=user.id).count()

    approved_works = Work.query.filter_by(
        user_id=user.id,
        status="approved"
    ).count()

    pending_works = Work.query.filter_by(
        user_id=user.id,
        status="pending"
    ).count()

    rejected_works = Work.query.filter_by(
        user_id=user.id,
        status="rejected"
    ).count()

    # APPLICATIONS COUNT
    total_applications = WorkApplication.query.filter_by(
        user_id=user.id
    ).count()

    return render_template(
        "owner/user_profile.html",

        user=user,

        works=works,

        total_works=total_works,

        approved_works=approved_works,

        pending_works=pending_works,

        rejected_works=rejected_works,

        total_applications=total_applications
    )


# =================================================
# ✏️ ADVANCED EDIT USER
# =================================================
@owner.route('/owner/user/edit/<int:id>', methods=["GET", "POST"])
@owner_only
def edit_user(id):

    user = User.query.get_or_404(id)

    if request.method == "POST":

        try:

            # ================= BASIC =================
            user.name = request.form.get("name")
            user.phone = request.form.get("phone")
            user.role = request.form.get("role")
            user.status = request.form.get("status")

            # ================= OPTIONAL =================
            if hasattr(user, "email"):
                user.email = request.form.get("email")

            if hasattr(user, "address"):
                user.address = request.form.get("address")

            if hasattr(user, "bio"):
                user.bio = request.form.get("bio")

            # ================= SAVE =================
            db.session.commit()

            socketio.emit("notify", {
                "type": "info",
                "message": f"{user.name} updated successfully ✏️"
            })

            flash("User updated successfully", "success")

            return redirect('/owner/dashboard')

        except Exception as e:

            db.session.rollback()

            flash(f"Error: {str(e)}", "danger")

            return redirect(f'/owner/user/edit/{id}')

    return render_template(
        "owner/edit_user.html",
        user=user
    )



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


@owner.route("/withdraw/approve/<int:id>")
def approve_withdraw(id):
    ...
    try:

        owner_id = session.get("user_id")

        req = WithdrawRequest.query.get(id)

        # ================= VALIDATION =================

        if not req:
            return "Request not found"

        if req.status != "pending":
            return "Invalid request"

        user = User.query.get(req.user_id)

        if not user:
            return "User not found"

        # ================= DOUBLE SAFETY =================

        if req.amount <= 0:
            return "Invalid amount"

        if (user.wallet_balance or 0) < req.amount:
            return "Insufficient wallet balance"

        # ================= UPDATE WALLET =================

        user.wallet_balance = float(user.wallet_balance or 0) - req.amount

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        # ================= UPDATE REQUEST =================

        req.status = "approved"
        req.approved_by = owner_id
        req.processed_at = datetime.utcnow()

        db.session.commit()

        # ================= NOTIFICATION =================

        send_notification(
            user_id=user.id,
            title="Withdraw Approved",
            message=f"₹{req.amount} has been approved",
            type="withdraw",
            icon="check",
            action_url="/wallet",
            priority="high"
        )

        return "Withdraw Approved"

    except Exception as e:

        db.session.rollback()
        print("Approve Withdraw Error:", e)
        return "Error occurred"

@owner.route("/withdraw/reject/<int:id>")
def reject_withdraw(id):
    ...
    try:

        owner_id = session.get("user_id")

        req = WithdrawRequest.query.get(id)

        # ================= VALIDATION =================

        if not req:
            return "Request not found"

        if req.status != "pending":
            return "Already processed"

        # ================= UPDATE REQUEST =================

        req.status = "rejected"
        req.approved_by = owner_id
        req.processed_at = datetime.utcnow()

        db.session.commit()

        # ================= NOTIFICATION =================

        send_notification(
            user_id=req.user_id,
            title="Withdraw Rejected",
            message=f"₹{req.amount} withdraw request rejected",
            type="withdraw",
            icon="warning",
            action_url="/wallet",
            priority="high"
        )

        return "Withdraw Rejected"

    except Exception as e:

        db.session.rollback()
        print("Reject Withdraw Error:", e)
        return "Error occurred"

# =====================================================
# OWNER REQUIRED
# =====================================================

def owner_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/auth/login")

        if session.get("role") != "owner":
            return "Access denied"

        return f(*args, **kwargs)

    return wrapper


# =====================================================
# WITHDRAW LIST (UPGRADED)
# =====================================================

@owner.route("/withdraws")
def withdraw_list():
    ...

    status = request.args.get("status")   # pending/approved/rejected
    page = request.args.get("page", 1, type=int)
    per_page = 20

    query = WithdrawRequest.query

    # ================= FILTER =================

    if status:
        query = query.filter_by(status=status)

    # ================= PAGINATION =================

    withdraws = query.order_by(
        WithdrawRequest.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template(
        "owner/withdraw_list.html",
        withdraws=withdraws,
        status=status
    )


from datetime import datetime


@owner.route("/withdraw/paid/<int:id>")
def mark_paid(id):
    ...

    try:

        req = WithdrawRequest.query.get(id)

        if not req:
            return "Not found"

        if req.status != "approved":
            return "Only approved requests can be marked paid"

        if req.payment_status == "paid":
            return "Already marked as paid"

        # ================= UPDATE =================

        req.payment_status = "paid"
        req.processed_at = datetime.utcnow()

        db.session.commit()

        return "Marked as Paid successfully"

    except Exception as e:

        db.session.rollback()
        print("Mark Paid Error:", e)
        return "Error occurred"
