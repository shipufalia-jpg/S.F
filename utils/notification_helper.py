from extensions import db, socketio

from models.notification import Notification

from datetime import datetime


def send_notification(

    user_id,

    title,

    message,

    type="general",

    icon="bell",

    image=None,

    action_url=None,

    sender_id=None,

    priority="normal",

    category=None,

    sound="default",

    device="web",

    socket_room=None,

    is_broadcast=False,

    is_pinned=False,

    expires_at=None,

    realtime=True
):

    try:

        # =====================================
        # CREATE NOTIFICATION
        # =====================================

        notification = Notification(

            user_id=user_id,

            sender_id=sender_id,

            title=title,

            message=message,

            type=type,

            icon=icon,

            image=image,

            action_url=action_url,

            priority=priority,

            category=category,

            sound=sound,

            device=device,

            socket_room=socket_room,

            is_broadcast=is_broadcast,

            is_pinned=is_pinned,

            expires_at=expires_at,

            is_sent=realtime,

            delivery_status="sent"
        )

        # =====================================
        # SAVE DATABASE
        # =====================================

        db.session.add(notification)

        db.session.commit()

        # =====================================
        # REALTIME SOCKET EVENT
        # =====================================

        if realtime:

            socketio.emit(

                "new_notification",

                {

                    "id": notification.id,

                    "title": notification.title,

                    "message": notification.message,

                    "type": notification.type,

                    "icon": notification.icon,

                    "image": notification.image,

                    "action_url": notification.action_url,

                    "priority": notification.priority,

                    "category": notification.category,

                    "sound": notification.sound,

                    "is_pinned": notification.is_pinned,

                    "created_at": notification.created_at.strftime(
                        "%d %b %Y %I:%M %p"
                    )

                },

                room=socket_room or f"user_{user_id}"
            )

        return notification

    except Exception as e:

        db.session.rollback()

        print("\n===================================")
        print("NOTIFICATION ERROR")
        print(e)
        print("===================================\n")

        return None
