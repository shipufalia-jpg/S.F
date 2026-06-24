
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
from routes.chamber.auth import chamber
from routes.doctor import doctor_bp

import cloudinary


# ================= LOGIN MANAGER =================
login_manager = LoginManager()
login_manager.login_view = "auth.login"


# ================= DB FIX FUNCTION =================


def fix_db(app):

    with app.app_context():

            
# ================= APP FACTORY =================
def create_app():

    app = Flask(__name__)
    
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
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
        cloud_name=os.getenv(
            "CLOUDINARY_CLOUD_NAME"
        ),
        api_key=os.getenv(
            "CLOUDINARY_API_KEY"
        ),
        api_secret=os.getenv(
            "CLOUDINARY_API_SECRET"
        ),
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
    app.register_blueprint(chamber)
    app.register_blueprint(
    doctor_bp
    )   
    

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
