from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

db = SQLAlchemy()

socketio = SocketIO(
    cors_allowed_origins=os.environ.get("CORS_ORIGINS", "*"),
    async_mode="threading",
    ping_timeout=20,
    ping_interval=25
)

limiter = Limiter(
    key_func=get_remote_address
)
