from flask_socketio import emit, join_room
from flask import session
from extensions import socketio, db
from models.chat import Chat


# ================= JOIN ROOM =================
@socketio.on("join")
def join(data):

    user_id = int(data.get("user_id"))

    join_room(f"chat_user_{user_id}")

# ================= SEND MESSAGE =================
@socketio.on("send_message")
def send_message(data):

    sender_id = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    message = data.get("message")

    if not sender_id or not receiver_id or not message:
        return

    chat = Chat(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message.strip()
    )

    db.session.add(chat)
    db.session.commit()

    room = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

    emit("receive_message", {
        "id": chat.id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": chat.message
    }, room=room)
