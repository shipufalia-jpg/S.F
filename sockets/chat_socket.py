from flask_socketio import emit, join_room
from flask import session
from extensions import socketio, db
from models.chat import Chat

@socketio.on("connect")
def connect():
    print("Socket Connected:", request.sid)

@socketio.on("send_message")
def send_message(data):

    if not current_user.is_authenticated:
        return

    try:
        receiver_id = int(data.get("receiver_id"))
        message = data.get("message")

        if not message:
            return

        chat = Chat(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=message.strip()
        )

        db.session.add(chat)
        db.session.commit()

        # 🔥 SEND TO ALL CLIENTS (SIMPLE)
        socketio.emit("receive_message", {
            "sender_id": current_user.id,
            "receiver_id": receiver_id,
            "message": chat.message
        })

        print("MESSAGE SENT")

    except Exception as e:
        print("ERROR:", e)
