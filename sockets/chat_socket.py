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
        sender_id = session.get("user_id")

        print("SESSION:", dict(session))
        print("SENDER:", sender_id)

        if not sender_id:
            print("NO SESSION USER")
            return

        receiver_id = data.get("receiver_id")
        message = data.get("message")

        print("DATA:", receiver_id, message)

        chat = Chat(
            sender_id=int(sender_id),
            receiver_id=int(receiver_id),
            message=message.strip()
        )

        db.session.add(chat)
        db.session.commit()

        print("✅ SAVED CHAT:", chat.id)

    except Exception as e:
        db.session.rollback()
        print("❌ CHAT ERROR:", str(e))
