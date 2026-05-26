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

@notification_bp.route('/notification/read/<int:id>')
def mark_notification_read(id):

    user_id = session.get("user_id")

    notification = Notification.query.get_or_404(id)

    if notification.user_id != user_id:

        return redirect('/notifications')

    notification.is_read = True

    db.session.commit()

    return redirect(notification.action_url or '/notifications')
