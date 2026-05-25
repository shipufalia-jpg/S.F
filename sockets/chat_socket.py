from flask_socketio import emit, join_room
from flask import session
from extensions import socketio, db
from models.chat import Chat


# ================= JOIN ROOM =================
@socketio.on("join")
def handle_join(data):

    if not current_user.is_authenticated:
        return

    other_user_id = int(data.get("user_id"))
    user_id = current_user.id

    room = f"chat_{min(user_id, other_user_id)}_{max(user_id, other_user_id)}"

    join_room(room)

    print("JOINED ROOM:", room)
        
# ================= SEND MESSAGE =================
@socketio.on("send_message")
def send_message(data):

    if not current_user.is_authenticated:
        return

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

    room = f"chat_{min(chat.sender_id, receiver_id)}_{max(chat.sender_id, receiver_id)}"

    emit("receive_message", {
        "sender_id": chat.sender_id,
        "receiver_id": receiver_id,
        "message": chat.message,
        "created_at": str(chat.created_at)
    }, room=room)

    print("SENT ROOM:", room)
