from flask import (
    Blueprint,
    session,
    redirect,
    render_template
)
from sqlalchemy import or_, and_, func
from datetime import datetime
from models.user import User
from models.profile import Profile
from models.chat import Chat
from models.work_model import Work
from extensions import db
from decorators.auth import role_required
from models.live_media import LiveMedia
from extensions import db
from functools import wraps
from flask import request

user = Blueprint("user", __name__, url_prefix="/user")


# =========================================================
# USER LIVE TV
# =========================================================

@user.route("/live-tv")
def user_live_tv():

    role = session.get("role", "user")
    country = session.get("country")
    language = session.get("language")

    now = datetime.utcnow()

    medias = LiveMedia.query.filter(

        # ACTIVE
        LiveMedia.is_active.is_(True),

        # NOT DELETED
        LiveMedia.is_deleted.is_(False),

        # APPROVED
        LiveMedia.is_approved.is_(True),

        # ROLE FILTER
        (
            (LiveMedia.target_role == "all") |
            (LiveMedia.target_role == role)
        ),

        # SCHEDULE START
        (
            (LiveMedia.start_time == None) |
            (LiveMedia.start_time <= now)
        ),

        # SCHEDULE END
        (
            (LiveMedia.end_time == None) |
            (LiveMedia.end_time >= now)
        )

    ).order_by(

        # FORCE SHOW FIRST
        LiveMedia.force_show.desc(),

        # FEATURED FIRST
        LiveMedia.is_featured.desc(),

        # DISPLAY ORDER
        LiveMedia.display_order.asc(),

        # LATEST
        LiveMedia.id.desc()

    ).all()

    # =====================================================
    # AUTO VIEW UPDATE
    # =====================================================

    for media in medias:
        media.total_views += 1

    db.session.commit()

    # =====================================================
    # FORCE POPUP
    # =====================================================

    force_popup = next(
        (
            m for m in medias
            if m.force_show and m.show_popup
        ),
        None
    )

    # =====================================================
    # LIVE MEDIA
    # =====================================================

    live_media = next(
        (
            m for m in medias
            if m.is_live and m.live_status == "live"
        ),
        None
    )

    # =====================================================
    # BANNERS
    # =====================================================

    banners = [
        m for m in medias
        if m.media_type == "banner"
    ]

    # =====================================================
    # VIDEOS
    # =====================================================

    videos = [
        m for m in medias
        if m.media_type == "video"
    ]

    # =====================================================
    # AUDIOS
    # =====================================================

    audios = [
        m for m in medias
        if m.media_type == "audio"
    ]

    # =====================================================
    # POPUPS
    # =====================================================

    popups = [
        m for m in medias
        if m.show_popup
    ]

    # =====================================================
    # FLOATING PLAYER
    # =====================================================

    floating_player = next(
        (
            m for m in medias
            if m.floating_mode
        ),
        None
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render_template(

        "user/live_tv.html",

        medias=medias,

        live_media=live_media,

        banners=banners,

        videos=videos,

        audios=audios,

        popups=popups,

        floating_player=floating_player,

        force_popup=force_popup,

        total_medias=len(medias),

        total_videos=len(videos),

        total_audios=len(audios),

        total_banners=len(banners),

        now=now
    )


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
# =================================================
# 💬 CHAT SYSTEM
# =================================================

@user.route("/chat/<int:user_id>")
def chat(user_id):

    current_user_id = int(session.get("user_id"))

    receiver = User.query.get_or_404(user_id)

    messages = Chat.query.filter(
        ((Chat.sender_id == current_user_id) & (Chat.receiver_id == user_id)) |
        ((Chat.sender_id == user_id) & (Chat.receiver_id == current_user_id))
    ).order_by(Chat.id.asc()).all()

    return render_template(
        "chat.html",
        receiver=receiver,
        messages=messages,
        current_user_id=current_user_id
    )

@user.route("/inbox")
def inbox():

    user_id = int(session.get("user_id"))

    chats = Chat.query.filter(
        (Chat.sender_id == user_id) | (Chat.receiver_id == user_id)
    ).order_by(Chat.id.desc()).all()

    inbox_data = {}

    for c in chats:

        other = c.receiver_id if c.sender_id == user_id else c.sender_id

        if other not in inbox_data:
            inbox_data[other] = {
                "user_id": other,
                "last_message": c.message
            }

    return render_template("inbox.html", inbox=inbox_data.values())


# =====================================================
# LOGIN REQUIRED DECORATOR
# =====================================================

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/auth/login")

        return f(*args, **kwargs)

    return wrapper


# =====================================================
# WALLET DASHBOARD (UPGRADED)
# =====================================================

@user.route("/wallet")
@login_required
def wallet():

    user_id = session.get("user_id")

    # ================= GET USER =================

    user = User.query.get_or_404(user_id)

    # ================= FILTER PARAMS =================

    tx_type = request.args.get("type")  # credit / debit / transfer / withdraw
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # ================= BASE QUERY =================

    query = Transaction.query.filter_by(
        user_id=user_id
    )

    # ================= FILTER BY TYPE =================

    if tx_type:
        query = query.filter_by(type=tx_type)

    # ================= PAGINATION =================

    transactions = query.order_by(
        Transaction.id.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # ================= CALCULATIONS =================

    wallet_balance = float(user.wallet_balance or 0)

    total_credit = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter_by(
        user_id=user_id,
        type="credit"
    ).scalar() or 0

    total_debit = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter_by(
        user_id=user_id,
        type="debit"
    ).scalar() or 0

    # ================= RESPONSE =================

    return render_template(
        "wallet.html",
        user=user,
        wallet_balance=wallet_balance,
        transactions=transactions,
        total_credit=total_credit,
        total_debit=total_debit,
        tx_type=tx_type
)


