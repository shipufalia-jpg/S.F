# =========================================
# routes/booking.py
# PRODUCTION VERSION + NOTIFICATION SYSTEM
# =========================================

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    abort,
    flash,
    request,
    url_for
)

from sqlalchemy import desc

from extensions import db

from models.booking import Booking
from models.user import User
from models.work_model import Work

from permissions import (
    is_admin,
    is_super_admin,
    is_owner,
    can_manage_booking
)

from utils.notification_helper import send_notification


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
# CREATE BOOKING
# =========================================

@booking.route('/create/<int:work_id>', methods=['POST'])
def create_booking(work_id):

    if not login_required():
        return redirect("/auth/login")

    user_id = session.get("user_id")

    # =====================================
    # FIND WORK
    # =====================================

    work = Work.query.get_or_404(work_id)

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

        work_id=work.id,

        status="pending",

        is_active=False
    )

    db.session.add(booking_data)

    db.session.commit()

    # =====================================
    # USER NOTIFICATION
    # =====================================

    send_notification(

        user_id=user_id,

        title="Booking Created",

        message="Your booking request submitted successfully.",

        type="booking",

        icon="briefcase",

        priority="normal",

        action_url="/my-bookings"
    )

    # =====================================
    # OWNER NOTIFICATION
    # =====================================

    send_notification(

        user_id=owner_id,

        sender_id=user_id,

        title="New Booking Request",

        message="Someone booked your work.",

        type="booking",

        icon="briefcase",

        priority="high",

        action_url="/owner/bookings"
    )

    flash(
        "Booking created successfully",
        "success"
    )

    return redirect("/my-bookings")


# =========================================
# ADMIN BOOKINGS
# =========================================

@booking.route("/bookings")
def admin_bookings():

    if not login_required():
        return redirect("/auth/login")

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

    # =====================================
    # NOTIFICATION
    # =====================================

    send_notification(

        user_id=booking_data.user_id,

        title="Booking Approved",

        message="Your booking has been approved.",

        type="approve",

        icon="check-circle",

        priority="high",

        action_url="/my-bookings"
    )

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

    # =====================================
    # NOTIFICATION
    # =====================================

    send_notification(

        user_id=booking_data.user_id,

        title="Booking Rejected",

        message="Sorry, your booking has been rejected.",

        type="reject",

        icon="x-circle",

        priority="high",

        action_url="/my-bookings"
    )

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

    # =====================================
    # NOTIFICATION
    # =====================================

    send_notification(

        user_id=booking_data.user_id,

        title="Booking Blocked",

        message="Your booking has been blocked.",

        type="block",

        icon="ban",

        priority="high",

        action_url="/my-bookings"
    )

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

    # =====================================
    # NOTIFICATION
    # =====================================

    send_notification(

        user_id=booking_data.user_id,

        title="Booking Unblocked",

        message="Your booking has been unblocked.",

        type="general",

        icon="check-circle",

        priority="normal",

        action_url="/my-bookings"
    )

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

    # =====================================
    # NOTIFICATION
    # =====================================

    send_notification(

        user_id=booking_data.user_id,

        title="Booking Deleted",

        message="Your booking has been deleted.",

        type="warning",

        icon="trash",

        priority="high",

        action_url="/my-bookings"
    )

    flash(
        "Booking deleted successfully",
        "danger"
    )

    return redirect(request.referrer or "/bookings")

# =========================================
# OWNER FULL BOOKING CONTROL
# PRODUCTION VERSION + NOTIFICATION SYSTEM
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

    search = request.args.get(
        "search",
        ""
    ).strip()

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
        per_page=per_page,
        error_out=False
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
    # OWNER NOTIFICATIONS
    # =====================================

    owner_notifications = Notification.query.filter_by(

        user_id=session.get("user_id"),

        is_deleted=False

    ).order_by(

        desc(Notification.id)

    ).limit(10).all()

    # =====================================
    # UNREAD COUNT
    # =====================================

    unread_notifications = Notification.query.filter_by(

        user_id=session.get("user_id"),

        is_read=False,

        is_deleted=False

    ).count()

    # =====================================
    # AUTO MARK AS READ
    # =====================================

    Notification.query.filter_by(

        user_id=session.get("user_id"),

        is_read=False

    ).update({

        "is_read": True

    })

    db.session.commit()

    # =====================================
    # RENDER TEMPLATE
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

        search=search,

        owner_notifications=owner_notifications,

        unread_notifications=unread_notifications
    )
