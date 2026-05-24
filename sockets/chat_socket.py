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
def send_message(data):

    sender_id = session.get("user_id")

    print("SESSION USER:", sender_id)  # DEBUG

    if not sender_id:
        return

    receiver_id = data.get("receiver_id")
    message = data.get("message")

    print("DATA:", receiver_id, message)

    if not receiver_id or not message:
        return

    chat = Chat(
        sender_id=int(sender_id),
        receiver_id=int(receiver_id),
        message=message.strip()
    )

    db.session.add(chat)
    db.session.commit()

    print("SAVED CHAT ID:", chat.id)

    emit("receive_message", {
        "id": chat.id,
        "sender_id": chat.sender_id,
        "receiver_id": receiver_id,
        "message": chat.message,
        "created_at": str(chat.created_at)
    }, broadcast=True)
