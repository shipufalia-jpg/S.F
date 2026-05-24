from flask_socketio import emit, join_room
from flask import session

from extensions import socketio, db
from models.chat import Chat


# =========================================================
# JOIN ROOM
# =========================================================

@socketio.on("join")
def handle_join(data):

    user_id = data.get("user_id")

    if not user_id:
        return

    join_room(f"user_{user_id}")

    print(f"Joined: user_{user_id}")


# =========================================================
# SEND MESSAGE
# =========================================================

@socketio.on("send_message")
def handle_send_message(data):

    sender_id = session.get("user_id")

    if not sender_id:
        return

    receiver_id = data.get("receiver_id")
    message = data.get("message")

    if not receiver_id or not message:
        return

    # SAVE CHAT
    chat = Chat(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message
    )

    db.session.add(chat)
    db.session.commit()

    payload = {
        "id": chat.id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message,
        "created_at": str(chat.created_at)
    }

    # RECEIVER
    socketio.emit(
        "receive_message",
        payload,
        room=f"user_{receiver_id}"
    )

    # SENDER
    socketio.emit(
        "receive_message",
        payload,
        room=f"user_{sender_id}"
    )

    print("Message Sent:", payload)
