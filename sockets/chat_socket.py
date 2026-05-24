from flask_socketio import emit, join_room
from flask import session

from extensions import socketio, db
from models.chat import Chat

@socketio.on("join")
def handle_join(data):

    user_id = data.get("user_id")

    if not user_id:
        return

    join_room(f"user_{user_id}")

    print(f"Joined: user_{user_id}")


@socketio.on("send_message")
def handle_send_message(data):

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    message = data.get("message")

    if not sender_id or not receiver_id or not message:
        return

    sender_id = int(sender_id)
    receiver_id = int(receiver_id)

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

    socketio.emit(
        "receive_message",
        payload,
        room=f"user_{receiver_id}"
    )

    print("Message Sent:", payload)
