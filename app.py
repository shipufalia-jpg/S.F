from gevent import monkey
monkey.patch_all()

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_login import LoginManager, current_user
from flask_socketio import emit, join_room
from sqlalchemy import text

from config import Config
from extensions import db, socketio
from flask_migrate import Migrate

from models.user import User
from models.chat import Chat
from models.work_model import Work
from models.work_application import WorkApplication
from models.notification import Notification

from routes.auth import auth
from routes.owner import owner
from routes.admin import admin_bp
from routes.super_admin import super_admin
from routes.user import user
from routes.main import main
from routes.work_routes import work
from routes.notification import notification_bp
from routes.live_media import live_media_bp
from routes.booking import booking
from routes.profile import profile_bp
from routes.admin_tools import admin_tools
from werkzeug.security import generate_password_hash
from routes.owner_tools import owner_tools
from routes.application_routes import application_bp
import cloudinary


# ================= LOGIN MANAGER =================
login_manager = LoginManager()
login_manager.login_view = "auth.login"


# ================= DB FIX FUNCTION =================

def fix_db(app):

    with app.app_context():

        try:

            # ================= WORKS TABLE FIX =================
            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS mobile VARCHAR(15);
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending';
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT FALSE;
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
            """))

            # ================= BOOKINGS TABLE FIX =================
            db.session.execute(text("""
                ALTER TABLE bookings
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
            """))

            db.session.execute(text("""
                ALTER TABLE bookings
                ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
            """))
            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS workers VARCHAR(100)
           """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS salary VARCHAR(100)
           """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS date VARCHAR(100)
           """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS time VARCHAR(100)
           """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS phone VARCHAR(20)
           """))

            db.session.commit()

            print("✅ DB FIXED SUCCESSFULLY")

        except Exception as e:

            db.session.rollback()
            print("DB FIX ERROR:", e)

# ================= APP FACTORY =================
def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # ================= UPLOAD FOLDER =================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_PATH = os.path.join(BASE_DIR, "static", "uploads", "live_media")

    os.makedirs(UPLOAD_PATH, exist_ok=True)

    # ================= LOGIN =================
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # DATABASE
    db.init_app(app)

    # SOCKET IO
    socketio.init_app(app, cors_allowed_origins="*", async_mode="gevent")

    # MIGRATION
    Migrate(app, db)

    # CLOUDINARY
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dbasxrygb"),
        api_key=os.getenv("CLOUDINARY_API_KEY", "618897129349859"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET", "5Q0-0gFHzhU48-CO6U1uPFnFiXQ"),
        secure=True
    )

    # BLUEPRINTS
    app.register_blueprint(auth)
    app.register_blueprint(owner)
    app.register_blueprint(admin_bp)
    app.register_blueprint(super_admin)
    app.register_blueprint(user)
    app.register_blueprint(main)
    app.register_blueprint(work)
    app.register_blueprint(booking)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_tools)
    app.register_blueprint(owner_tools)
    app.register_blueprint(application_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(live_media_bp)

    return app


app = create_app()

# ================= DB INIT =================
with app.app_context():
    db.create_all()
    fix_db(app)   # 🔥 AUTO FIX RUN HERE


# ================= SOCKET EVENTS =================

@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        try:
            current_user.is_online = True
            db.session.commit()
        except:
            pass


@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        try:
            current_user.is_online = False
            db.session.commit()
        except:
            pass


@socketio.on("join")
def on_join(data):
    if not current_user.is_authenticated:
        return

    try:
        other_user = int(data.get("user_id"))
        user_id = current_user.id

        room = f"chat_{min(user_id, other_user)}_{max(user_id, other_user)}"
        join_room(room)

    except:
        pass


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

        room = f"chat_{min(chat.sender_id, receiver_id)}_{max(chat.sender_id, receiver_id)}"

        emit("receive_message", {
            "id": chat.id,
            "sender_id": chat.sender_id,
            "receiver_id": receiver_id,
            "message": chat.message,
            "created_at": str(chat.created_at)
        }, room=room)

    except Exception as e:
        print("Chat Error:", e)




# ================= RUN =================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
