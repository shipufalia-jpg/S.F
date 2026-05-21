from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os

db = SQLAlchemy()

socketio = SocketIO(
    cors_allowed_origins=os.environ.get("CORS_ORIGINS", "*"),
    async_mode="threading",   # ✅ FIXED (eventlet remove)
    ping_timeout=20,
    ping_interval=25
)