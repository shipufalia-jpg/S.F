from flask_socketio import emit, join_room
from flask import session
from extensions import socketio, db
from models.chat import Chat


# ================= JOIN ROOM =================
@socketio.on("join")
def handle_join(data):

    user_id = data.get("user_id")

    if not user_id:
        return

    room = f"user_{user_id}"
    join_room(room)

    print(f"Joined: {room}")


# ================= SEND MESSAGE =================
@socketio.on("send_message")
def send_message(data):

    sender_id = session.get("user_id")

    print("SESSION USER:", sender_id)

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

    payload = {
        "id": chat.id,
        "sender_id": chat.sender_id,
        "receiver_id": chat.receiver_id,
        "message": chat.message,
        "created_at": str(chat.created_at)
    }

    # 🔥 SEND TO RECEIVER ROOM
    socketio.emit(
        "receive_message",
        payload,
        room=f"user_{receiver_id}"
    )

    # 🔥 SEND TO SENDER ROOM
    socketio.emit(
        "receive_message",
        payload,
        room=f"user_{sender_id}"
    )
