# =========================================
# routes/booking.py
# PRODUCTION VERSION
# =========================================

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    abort,
    flash,
    request
)

from sqlalchemy import desc

from extensions import db

from models.booking import Booking
from models.user import User
from models.work_model import Work
from flask_login import current_user

from permissions import (
    is_admin,
    is_super_admin,
    is_owner,
    can_manage_booking
)

booking = Blueprint(
    "booking",
    __name__
)


# =========================================
# LOGIN CHECK
# =========================================

def login_required():

    if not session.get("user_id"):
        return False

    return True


# =========================================
# USER BOOKINGS
# USER CAN SEE OWN BOOKINGS
# =========================================

@booking.route("/my-bookings")
def my_bookings():

    if not login_required():
        return redirect("/auth/login")

    bookings = Booking.query.filter_by(
        user_id=session.get("user_id"),
        is_deleted=False
    ).order_by(
        desc(Booking.id)
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

# =========================================
# USER CREATE BOOKING
# =========================================
@booking.route('/create/<int:work_id>', methods=['POST'])
def create_booking(work_id):

    work = Work.query.get_or_404(work_id)

    booking = Booking(
        user_id=current_user.id,
        owner_id=work.user_id,
        work_id=work.id
    )

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for('profile.view_profile', user_id=work.user_id))

    # =====================================
    # FIND WORK
    # =====================================

    work = Work.query.get_or_404(work_id)

    # =====================================
    # OWNER ID
    # =====================================

    owner_id = work.user_id

    # =====================================
    # PREVENT SELF BOOKING
    # =====================================

    if owner_id == user_id:

        flash(
            "You cannot book your own work",
            "warning"
        )

        return redirect(request.referrer or "/")

    # =====================================
    # CHECK EXISTING BOOKING
    # =====================================

    existing = Booking.query.filter_by(
        user_id=user_id,
        owner_id=owner_id,
        is_deleted=False
    ).first()

    if existing:

        flash(
            "Already booked",
            "info"
        )

        return redirect(request.referrer or "/")

    # =====================================
    # CREATE BOOKING
    # =====================================

    booking_data = Booking(
        user_id=user_id,
        owner_id=owner_id,
        status="pending",
        is_active=False
    )

    db.session.add(booking_data)

    db.session.commit()

    flash(
        "Booking created successfully",
        "success"
    )

    return redirect("/my-bookings")


# =========================================
# ADMIN BOOKINGS
# ADMIN CAN SEE OWN USERS BOOKINGS
# =========================================

@booking.route("/bookings")
def admin_bookings():

    if not login_required():
        return redirect("/auth/login")

    # =====================================
    # OWNER FULL ACCESS
    # =====================================

    if is_owner():

        bookings = Booking.query.filter_by(
            is_deleted=False
        ).order_by(
            desc(Booking.id)
        ).all()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    # =====================================
    # SUPER ADMIN
    # =====================================

    if is_super_admin():

        admins = User.query.filter_by(
            role="admin",
            created_by=session.get("user_id"),
            is_deleted=False
        ).all()

        admin_ids = [a.id for a in admins]

        users = User.query.filter(
            User.created_by.in_(admin_ids),
            User.role == "user",
            User.is_deleted == False
        ).all()

        user_ids = [u.id for u in users]

        bookings = Booking.query.filter(
            Booking.user_id.in_(user_ids),
            Booking.is_deleted == False
        ).order_by(
            desc(Booking.id)
        ).all()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    # =====================================
    # ADMIN
    # =====================================

    if is_admin():

        users = User.query.filter_by(
            created_by=session.get("user_id"),
            role="user",
            is_deleted=False
        ).all()

        user_ids = [u.id for u in users]

        bookings = Booking.query.filter(
            Booking.user_id.in_(user_ids),
            Booking.is_deleted == False
        ).order_by(
            desc(Booking.id)
        ).all()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    # =====================================
    # NORMAL USER NOT ALLOWED
    # =====================================

    abort(403)


# =========================================
# APPROVE BOOKING
# =========================================

@booking.route(
    "/booking/approve/<int:id>",
    methods=["POST"]
)
def approve_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "approved"

    booking_data.is_active = True

    booking_data.approved_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking approved successfully",
        "success"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# REJECT BOOKING
# =========================================

@booking.route(
    "/booking/reject/<int:id>",
    methods=["POST"]
)
def reject_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "rejected"

    booking_data.is_active = False

    booking_data.rejected_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking rejected successfully",
        "warning"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# BLOCK BOOKING
# =========================================

@booking.route(
    "/booking/block/<int:id>",
    methods=["POST"]
)
def block_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "blocked"

    booking_data.is_active = False

    booking_data.blocked_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking blocked successfully",
        "danger"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# UNBLOCK BOOKING
# =========================================

@booking.route(
    "/booking/unblock/<int:id>",
    methods=["POST"]
)
def unblock_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "pending"

    booking_data.is_active = False

    db.session.commit()

    flash(
        "Booking unblocked successfully",
        "success"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# DELETE BOOKING
# =========================================

@booking.route(
    "/booking/delete/<int:id>",
    methods=["POST"]
)
def delete_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "deleted"

    booking_data.is_deleted = True

    booking_data.deleted_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking deleted successfully",
        "danger"
    )

    return redirect(request.referrer or "/bookings")

# =========================================
# OWNER FULL BOOKING CONTROL
# PRODUCTION VERSION
# =========================================

@booking.route("/owner/bookings")
def owner_bookings():

    # =====================================
    # LOGIN CHECK
    # =====================================

    if not login_required():
        return redirect("/auth/login")

    # =====================================
    # ONLY OWNER ACCESS
    # =====================================

    if not is_owner():
        abort(403)

    # =====================================
    # PAGINATION
    # =====================================

    page = request.args.get("page", 1, type=int)
    per_page = 20

    # =====================================
    # SEARCH
    # =====================================

    search = request.args.get("search", "").strip()

    # =====================================
    # BASE QUERY
    # =====================================

    query = Booking.query.filter_by(
        is_deleted=False
    )

    # =====================================
    # SEARCH FILTER
    # =====================================

    if search:

        query = query.join(User).filter(
            User.name.ilike(f"%{search}%")
        )

    # =====================================
    # BOOKINGS
    # =====================================

    bookings = query.order_by(
        desc(Booking.id)
    ).paginate(
        page=page,
        per_page=per_page
    )

    # =====================================
    # TOTAL COUNTS
    # =====================================

    total_bookings = Booking.query.filter_by(
        is_deleted=False
    ).count()

    pending_bookings = Booking.query.filter_by(
        status="pending",
        is_deleted=False
    ).count()

    approved_bookings = Booking.query.filter_by(
        status="approved",
        is_deleted=False
    ).count()

    rejected_bookings = Booking.query.filter_by(
        status="rejected",
        is_deleted=False
    ).count()

    blocked_bookings = Booking.query.filter_by(
        status="blocked",
        is_deleted=False
    ).count()

    active_bookings = Booking.query.filter_by(
        is_active=True,
        is_deleted=False
    ).count()

    # =====================================
    # RECENT BOOKINGS
    # =====================================

    recent_bookings = Booking.query.filter_by(
        is_deleted=False
    ).order_by(
        desc(Booking.id)
    ).limit(5).all()

    # =====================================
    # RENDER
    # =====================================

    return render_template(

        "owner_bookings.html",

        bookings=bookings.items,

        pagination=bookings,

        recent_bookings=recent_bookings,

        total_bookings=total_bookings,

        pending_bookings=pending_bookings,

        approved_bookings=approved_bookings,

        rejected_bookings=rejected_bookings,

        blocked_bookings=blocked_bookings,

        active_bookings=active_bookings,

        current_page=page,

        search=search
    )
