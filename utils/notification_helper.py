from models.notification import Notification
from extensions import db


def send_notification(
    user_id,
    title,
    message,
    type="general",
    icon="bell",
    action_url=None,
    sender_id=None,
    priority="normal",
    device="web"
):

    try:

        notification = Notification(

            user_id=user_id,
            sender_id=sender_id,

            title=title,
            message=message,

            type=type,
            icon=icon,

            action_url=action_url,

            priority=priority,

            device=device
        )

        db.session.add(notification)
        db.session.commit()

        return notification

    except Exception as e:

        db.session.rollback()

        print("Notification Error:", e)

        return None
