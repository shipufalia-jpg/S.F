from services.socket_service import socketio
from models.user import User
from extensions import db
from flask import session
from datetime import datetime
from flask_login import current_user
from models.chat import Chat


# ================= USER CONNECT =================
@socketio.on('connect')
def handle_connect():

    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)

        if user:
            user.is_online = True
            user.last_seen = datetime.utcnow()

            db.session.commit()


# ================= USER DISCONNECT =================
@socketio.on('disconnect')
def handle_disconnect():

    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)

        if user:
            user.is_online = False
            user.last_seen = datetime.utcnow()

            db.session.commit()