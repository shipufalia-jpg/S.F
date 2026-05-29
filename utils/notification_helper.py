from extensions import db, socketio
from models.notification import Notification


def send_notification(

    user_id,
    title,
    message,
    type="general",
    icon="bell",
    action_url=None,
    sender_id=None,
    priority="normal",
    device="web",
    realtime=True

):

    try:

        # ================= CREATE NOTIFICATION =================

        notification = Notification(

            user_id=user_id,
            sender_id=sender_id,
            title=title,
            message=message,

            type=type,
            icon=icon,

            action_url=action_url,
            priority=priority,
            device=device,

            is_sent=realtime

        )

        db.session.add(notification)
        db.session.flush()  # safer than commit first

        # ================= COMMIT =================

        db.session.commit()

        # ================= REALTIME SOCKET EVENT =================

        if realtime and socketio:

            socketio.emit(

                "notification:new",

                {

                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "icon": notification.icon,
                    "action_url": notification.action_url,
                    "priority": notification.priority,

                    "created_at": notification.created_at.isoformat()

                },

                room=f"user_{user_id}"

            )

        return notification

    except Exception as e:

        db.session.rollback()

        print("\n===================================")
        print("NOTIFICATION ERROR")
        print(e)
        print("===================================\n")

        return None
