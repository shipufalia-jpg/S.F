from flask_socketio import emit, join_room
from flask import session
from extensions import socketio, db
from models.chat import Chat


# ================= JOIN ROOM =================
@socketio.on("join")
def join(data):
    user_id = int(data.get("user_id"))
    join_room(f"user_{user_id}")
    print("JOINED:", user_id)
# ================= SEND MESSAGE =================
@socketio.on("send_message")
def send_message(data):

    sender_id = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    message = data.get("message")

    if not message:
        return

    # SAVE DB
    chat = Chat(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message.strip()
    )

    db.session.add(chat)
    db.session.commit()

    payload = {
        "id": chat.id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": chat.message
    }

    # SEND TO BOTH USERS (IMPORTANT)
    socketio.emit("receive_message", payload, room=f"user_{sender_id}")
    socketio.emit("receive_message", payload, room=f"user_{receiver_id}")
