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

    try:
        sender_id = data.get("sender_id")
        receiver_id = data.get("receiver_id")
        message = data.get("message")

        print("INCOMING:", sender_id, receiver_id, message)

        if not sender_id or not receiver_id or not message:
            return

        chat = Chat(
            sender_id=int(sender_id),
            receiver_id=int(receiver_id),
            message=message.strip()
        )

        db.session.add(chat)
        db.session.commit()

        print("✅ MESSAGE SAVED:", chat.id)

        payload = {
            "id": chat.id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": message
        }

        # send to both users
        emit("receive_message", payload, broadcast=True)

    except Exception as e:
        db.session.rollback()
        print("❌ ERROR:", str(e))
