from flask import (
    Blueprint,
    session,
    redirect,
    render_template
)
from sqlalchemy import or_, and_, func
from models.user import User
from models.profile import Profile
from models.chat import Chat
from models.work_model import Work
from extensions import db
from decorators.auth import role_required

user = Blueprint("user", __name__, url_prefix="/user")


# =================================================
# 👤 USER DASHBOARD
# =================================================
@user.route('/dashboard')
@role_required("user")
def dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect('/auth/login')

    current_user_data = db.session.get(User, user_id)

    if not current_user_data:
        session.clear()
        return redirect('/auth/login')

    # ================= APPROVED WORKS =================
    works = (
        db.session.query(Work, User)
        .join(User, Work.user_id == User.id)
        .filter(Work.status == "approved")
        .order_by(Work.created_at.desc())
        .all()
    )

    # ================= PROFILES =================
    profiles = (
        Profile.query
        .join(User, Profile.user_id == User.id)
        .filter(Profile.user_id != user_id)
        .order_by(Profile.id.desc())
        .all()
    )

    # ================= STATS =================
    total_works = Work.query.filter_by(status="approved").count()
    total_profiles = Profile.query.count()

    return render_template(
        "user/dashboard.html",
        current_user=current_user_data,
        works=works,
        profiles=profiles,
        total_works=total_works,
        total_profiles=total_profiles
    )


# =================================================
# 👤 PUBLIC PROFILE VIEW
# =================================================
@user.route('/profile/<int:user_id>')
@role_required("user")
def public_profile(user_id):

    profile_user = User.query.get_or_404(user_id)

    profile = Profile.query.filter_by(user_id=user_id).first()

    works = Work.query.filter_by(user_id=user_id).order_by(
        Work.id.desc()
    ).all()

    return render_template(
        "public_profile.html",
        profile_user=profile_user,
        profile=profile,
        works=works
    )


# =================================================
# 💬 CHAT SYSTEM
# =================================================


@user.route("/chat/<int:user_id>")
@role_required("user")
def chat(user_id):

    current_user_id = session.get("user_id")

    # 🔒 login check
    if not current_user_id:
        return redirect("/auth/login")

    # 🔢 convert type (VERY IMPORTANT FIX)
    current_user_id = int(current_user_id)
    user_id = int(user_id)

    # 🚫 self chat block
    if current_user_id == user_id:
        return redirect("/user/dashboard")

    receiver = User.query.get_or_404(user_id)

    # 💬 GET MESSAGES (FIXED SAFE QUERY)
    messages = Chat.query.filter(
        or_(
            and_(
                Chat.sender_id == current_user_id,
                Chat.receiver_id == user_id
            ),
            and_(
                Chat.sender_id == user_id,
                Chat.receiver_id == current_user_id
            )
        )
    ).order_by(Chat.id.asc()).all()

    # 🐞 DEBUG (temporary)
    print("USER:", current_user_id, "CHAT WITH:", user_id)
    print("TOTAL MESSAGES:", len(messages))

    return render_template(
        "chat.html",
        receiver=receiver,
        messages=messages,
        current_user_id=current_user_id
)

@user.route("/inbox")
def inbox():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/auth/login")

    user_id = int(user_id)

    # শুধু latest message per user আনতে হবে
    subquery = db.session.query(
        Chat,
        func.max(Chat.created_at).label("last_time")
    ).filter(
        or_(
            Chat.sender_id == user_id,
            Chat.receiver_id == user_id
        )
    ).group_by(
        Chat.sender_id,
        Chat.receiver_id
    ).order_by(Chat.created_at.desc()).all()

    inbox_data = {}

    for chat, _ in subquery:

        other_user_id = chat.receiver_id if chat.sender_id == user_id else chat.sender_id

        if other_user_id not in inbox_data:
            inbox_data[other_user_id] = {
                "user_id": other_user_id,
                "last_message": chat.message,
                "time": chat.created_at,
                "unread": 0
            }

        if chat.receiver_id == user_id and not chat.is_read:
            inbox_data[other_user_id]["unread"] += 1

    return render_template("inbox.html", inbox=list(inbox_data.values()))


