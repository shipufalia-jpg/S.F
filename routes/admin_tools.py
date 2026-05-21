from flask import Blueprint, session, redirect
from extensions import db
from sqlalchemy import text
from models.user import User

admin_tools = Blueprint("admin_tools", __name__, url_prefix="/admin")


# ================= OWNER ONLY DB RESET =================
@admin_tools.route("/db-reset", methods=["POST"])
def db_reset():

    # 🔐 1. LOGIN CHECK
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    # 🔐 2. GET USER
    user = User.query.get(user_id)
    if not user:
        return "Unauthorized", 403

    # 🔐 3. ONLY OWNER ALLOWED
    if user.role != "owner":
        return "❌ Only Owner Can Reset Database", 403

    try:
        # 💣 FULL RESET
        db.session.execute(text("DROP SCHEMA public CASCADE;"))
        db.session.execute(text("CREATE SCHEMA public;"))
        db.session.commit()

        return "✅ OWNER RESET SUCCESSFUL"

    except Exception as e:
        db.session.rollback()
        return f"❌ RESET FAILED: {str(e)}", 500
