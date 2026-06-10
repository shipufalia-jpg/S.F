from gevent import monkey
monkey.patch_all()
import shutil
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
from routes.verification import verification
from routes.chamber.chamber import chamber_panel
from routes.admin_panel.chambers import admin_chambers
import cloudinary


# ================= LOGIN MANAGER =================
login_manager = LoginManager()
login_manager.login_view = "auth.login"


# ================= DB FIX FUNCTION =================

def fix_db(app):

    with app.app_context():

        try:

            # ================= WORKS TABLE =================
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

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS workers VARCHAR(100);
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS salary VARCHAR(100);
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS date VARCHAR(100);
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS time VARCHAR(100);
            """))

            db.session.execute(text("""
                ALTER TABLE works
                ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
            """))

            # ================= BOOKINGS TABLE =================
            db.session.execute(text("""
                ALTER TABLE bookings
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
            """))

            db.session.execute(text("""
                ALTER TABLE bookings
                ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
            """))

            # ================= USER TABLE (IMPORTANT FIX) =================
            db.session.execute(text("""
                ALTER TABLE "user"
                ADD COLUMN IF NOT EXISTS wallet_balance FLOAT DEFAULT 0;
            """))

            db.session.execute(text("""
                ALTER TABLE "user"
                ADD COLUMN IF NOT EXISTS total_earnings FLOAT DEFAULT 0;
            """))
            db.session.execute(text("""
                ALTER TABLE withdraw_requests
                ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) DEFAULT 'unpaid';
            """))

            db.session.execute(text("""
                ALTER TABLE withdraw_requests
                ADD COLUMN IF NOT EXISTS paid_by INTEGER;
            """))

            db.session.execute(text("""
                ALTER TABLE withdraw_requests
                ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP;
            """))

            db.session.execute(text("""
                ALTER TABLE withdraw_requests
                ADD COLUMN IF NOT EXISTS utr_number VARCHAR(100);
            """))

            db.session.execute(text("""
                ALTER TABLE withdraw_requests
                ADD COLUMN IF NOT EXISTS admin_note TEXT;
            """))

            db.session.execute(text("""
                ALTER TABLE "user"
                ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
            """))

            db.session.execute(text("""
                ALTER TABLE "user"
                ADD COLUMN IF NOT EXISTS verification_expiry TIMESTAMP;
            """))

            # ================= DOCTORS TABLE =================

            # 1. Ensure column exists
            db.session.execute(text("""
                ALTER TABLE doctors
                ADD COLUMN IF NOT EXISTS chamber_id INTEGER;
            """))

            # 2. Check and add foreign key safely (WITHOUT DO block)
            db.session.execute(text("""
                ALTER TABLE doctors
                ADD CONSTRAINT IF NOT EXISTS fk_doctors_chamber
                FOREIGN KEY (chamber_id)
                REFERENCES chambers(id)
                ON DELETE SET NULL;
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

    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

    # ================= LOGIN MANAGER =================
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    # ================= DB =================
    db.init_app(app)

    # ================= SOCKET IO =================
    socketio.init_app(app, cors_allowed_origins="*", async_mode="gevent")

    # ================= MIGRATION =================
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
    app.register_blueprint(verification)
    app.register_blueprint(chamber_panel)
    app.register_blueprint(admin_chambers)
    

    return app


app = create_app()

# ================= DB INIT =================
with app.app_context():
    db.create_all()
    fix_db(app)   # 🔥 AUTO FIX RUN HERE


# ================= RUN =================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
