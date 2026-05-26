from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    flash,
    jsonify
)

from sqlalchemy import desc

from extensions import db

from models.notification import Notification
from flask import request
from models.user import User
from utils.notification_helper import send_notification


notification_bp = Blueprint(
    'notification',
    __name__
)


# =========================================
# ALL NOTIFICATIONS
# =========================================

@notification_bp.route('/notifications')
def notifications():

    user_id = session.get("user_id")

    if not user_id:

        flash("Login required", "danger")

        return redirect('/auth/login')

    # get notifications
    notifications = Notification.query.filter_by(

        user_id=user_id,
        is_deleted=False

    ).order_by(

        desc(Notification.created_at)

    ).all()

    # unread count
    unread_count = Notification.query.filter_by(

        user_id=user_id,
        is_read=False,
        is_deleted=False

    ).count()

    # auto mark as read
    Notification.query.filter_by(

        user_id=user_id,
        is_read=False

    ).update({

        "is_read": True

    })

    db.session.commit()

    return render_template(

        "notifications.html",

        notifications=notifications,

        unread_count=unread_count
    )


# =========================================
# DELETE NOTIFICATION
# =========================================

@notification_bp.route('/notification/delete/<int:id>')
def delete_notification(id):

    user_id = session.get("user_id")

    notification = Notification.query.get_or_404(id)

    # security check
    if notification.user_id != user_id:

        flash("Access denied", "danger")

        return redirect('/notifications')

    # soft delete
    notification.is_deleted = True

    db.session.commit()

    flash("Notification deleted", "success")

    return redirect('/notifications')


# =========================================
# CLEAR ALL
# =========================================

@notification_bp.route('/notifications/clear')
def clear_notifications():

    user_id = session.get("user_id")

    Notification.query.filter_by(

        user_id=user_id

    ).update({

        "is_deleted": True

    })

    db.session.commit()

    flash("All notifications cleared", "success")

    return redirect('/notifications')


# =========================================
# UNREAD COUNT API
# =========================================

@notification_bp.route('/notifications/unread-count')
def unread_notification_count():

    user_id = session.get("user_id")

    count = Notification.query.filter_by(

        user_id=user_id,
        is_read=False,
        is_deleted=False

    ).count()

    return jsonify({

        "unread_count": count
    })


# =========================================
# MARK SINGLE READ
# =========================================
# =========================================
# BROADCAST NOTIFICATION
# =========================================

@notification_bp.route(

    "/owner/notification/broadcast",

    methods=["GET", "POST"]

)
def broadcast_notification():

    # LOGIN CHECK
    if not session.get("user_id"):

        flash("Login required", "danger")

        return redirect("/auth/login")

    # ROLE CHECK
    if session.get("role") not in [

        "owner",
        "admin"

    ]:

        flash("Access denied", "danger")

        return redirect("/")

    # POST
    if request.method == "POST":

        title = request.form.get("title")

        message = request.form.get("message")

        type = request.form.get(

            "type",

            "general"
        )

        priority = request.form.get(

            "priority",

            "normal"
        )

        target_role = request.form.get(

            "target_role",

            "all"
        )

        # VALIDATION
        if not title or not message:

            flash(

                "Title and message required",

                "danger"
            )

            return redirect(
                "/owner/notification/broadcast"
            )

        # USERS
        if target_role == "all":

            users = User.query.all()

        else:

            users = User.query.filter_by(

                role=target_role

            ).all()

        # SEND
        total_sent = 0

        for user in users:

            notification = send_notification(

                user_id=user.id,

                sender_id=session.get("user_id"),

                title=title,

                message=message,

                type=type,

                icon="bell",

                priority=priority
            )

            if notification:

                total_sent += 1

        flash(

            f"{total_sent} notifications sent",

            "success"
        )

        return redirect(
            "/owner/notification/broadcast"
        )

    return render_template(

        "broadcast_notification.html"
        )
    
@notification_bp.route('/notification/read/<int:id>')
def mark_notification_read(id):

    user_id = session.get("user_id")

    notification = Notification.query.get_or_404(id)

    if notification.user_id != user_id:

        return redirect('/notifications')

    notification.is_read = True

    db.session.commit()

    return redirect(notification.action_url or '/notifications')
