from flask import session
from extensions import db
from models.user import User
from datetime import datetime
from services.socket_service import socketio


# 🟢 USER CONNECT
@socketio.on('connect')
def handle_connect():

    user_id = session.get('user_id')

    if not user_id:
        return

    user = User.query.get(user_id)

    if user:
        user.is_online = True
        user.last_seen = None  # optional reset
        user.socket_id = request.sid if hasattr(request, "sid") else None

        db.session.commit()


# 🔴 USER DISCONNECT
@socketio.on('disconnect')
def handle_disconnect():

    user_id = session.get('user_id')

    if not user_id:
        return

    user = User.query.get(user_id)

    if user:
        user.is_online = False
        user.last_seen = datetime.utcnow()
        user.socket_id = None

        db.session.commit()
