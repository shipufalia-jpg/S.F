from flask import (
    Blueprint,
    session,
    redirect,
    render_template,
    flash
)
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import joinedload
from datetime import datetime, UTC
from models.user import User
from models.profile import Profile
from models.chat import Chat
from models.work_model import Work
from extensions import db
from decorators.auth import role_required
from models.live_media import LiveMedia

from functools import wraps
from flask import request
from models.transaction import Transaction
from models.appointment import Appointment
from models.payment_method import UserPaymentMethod
from models.site_setting import SiteSetting

user = Blueprint("user", __name__, url_prefix="/user")

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


# =========================================================
# USER LIVE TV
# =========================================================
@user.route("/live-tv")
def user_live_tv():

    role = session.get("role", "user")
    now = datetime.now(UTC)

    page = request.args.get(
        "page",
        1,
        type=int
    )

    medias = (
        LiveMedia.query
        .filter(
            LiveMedia.is_active.is_(True),
            LiveMedia.is_deleted.is_(False),
            LiveMedia.is_approved.is_(True),

            (
                (LiveMedia.target_role == "all") |
                (LiveMedia.target_role == role)
            ),

            (
                LiveMedia.start_time.is_(None) |
                (LiveMedia.start_time <= now)
            ),

            (
                LiveMedia.end_time.is_(None) |
                (LiveMedia.end_time >= now)
            )
        )
        .order_by(
            LiveMedia.force_show.desc(),
            LiveMedia.is_featured.desc(),
            LiveMedia.display_order.asc(),
            LiveMedia.id.desc()
        )
        .paginate(
            page=page,
            per_page=20,
            error_out=False
        )
    )

    live_media = None
    floating_player = None
    force_popup = None

    banners = []
    videos = []
    audios = []
    popups = []

    for media in medias.items:

        if (
            live_media is None
            and media.is_live
            and media.live_status == "live"
        ):
            live_media = media

        if (
            floating_player is None
            and media.floating_mode
        ):
            floating_player = media

        if (
            force_popup is None
            and media.force_show
            and media.show_popup
        ):
            force_popup = media

        if media.media_type == "banner":
            banners.append(media)

        elif media.media_type == "video":
            videos.append(media)

        elif media.media_type == "audio":
            audios.append(media)

        if media.show_popup:
            popups.append(media)

    return render_template(
        "user/live_tv.html",

        medias=medias.items,
        pagination=medias,

        live_media=live_media,
        floating_player=floating_player,
        force_popup=force_popup,

        banners=banners,
        videos=videos,
        audios=audios,
        popups=popups,

        total_medias=medias.total,
        total_banners=len(banners),
        total_videos=len(videos),
        total_audios=len(audios),

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
        return redirect("/auth/login")

    current_user_data = db.session.get(
        User,
        user_id
    )

    if not current_user_data:
        session.clear()
        return redirect("/auth/login")

    setting = SiteSetting.query.first()

    # ================= PAGINATION =================

    work_page = request.args.get(
        "work_page",
        1,
        type=int
    )

    profile_page = request.args.get(
        "profile_page",
        1,
        type=int
    )

    # ================= WORKS =================

    works = (
        db.session.query(
            Work,
            User
        )
        .join(
            User,
            Work.user_id == User.id
        )
        .filter(
            Work.status == "approved"
        )
        .order_by(
            Work.created_at.desc()
        )
        .paginate(
            page=work_page,
            per_page=20,
            error_out=False
        )
    )

    # ================= PROFILES =================

    profiles = (
        Profile.query
        .options(
            joinedload(Profile.user)
        )
        .filter(
            Profile.user_id != user_id
        )
        .order_by(
            Profile.id.desc()
        )
        .paginate(
            page=profile_page,
            per_page=20,
            error_out=False
        )
    )

    # ================= STATS =================

    total_works = (
        db.session.query(
            func.count(Work.id)
        )
        .filter(
            Work.status == "approved"
        )
        .scalar()
    )

    total_profiles = (
        db.session.query(
            func.count(Profile.id)
        )
        .scalar()
    )

    return render_template(
        "user/dashboard.html",

        current_user=current_user_data,

        works=works.items,
        works_pagination=works,

        profiles=profiles.items,
        profiles_pagination=profiles,

        total_works=total_works,
        total_profiles=total_profiles,

        setting=setting
    )
# =================================================
# 💬 CHAT SYSTEM
# =================================================
@user.route("/chat/<int:user_id>")
@login_required
def chat(user_id):

    current_user_id = session.get("user_id")

    page = request.args.get(
        "page",
        default=1,
        type=int
    )

    receiver = User.query.get_or_404(user_id)

    messages = (
        Chat.query
        .filter(
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
        )
        .order_by(Chat.id.desc())
        .paginate(
            page=page,
            per_page=50,
            error_out=False
        )
    )

    return render_template(
        "chat.html",
        receiver=receiver,
        messages=list(reversed(messages.items)),
        pagination=messages,
        current_user_id=current_user_id
    )
@user.route("/inbox")
@login_required
def inbox():

    user_id = session["user_id"]

    page = request.args.get(
        "page",
        1,
        type=int
    )

    chats = (
        Chat.query
        .filter(
            (Chat.sender_id == user_id) |
            (Chat.receiver_id == user_id)
        )
        .order_by(Chat.id.desc())
        .paginate(
            page=page,
            per_page=50,
            error_out=False
        )
    )

    inbox_data = {}
    user_cache = {}

    for chat in chats.items:

        other_id = (
            chat.receiver_id
            if chat.sender_id == user_id
            else chat.sender_id
        )

        if other_id not in inbox_data:

            if other_id not in user_cache:

                user_cache[other_id] = db.session.get(
                    User,
                    other_id
                )

            other_user = user_cache[other_id]

            inbox_data[other_id] = {
                "user_id": other_id,
                "name": (
                    other_user.name
                    if other_user
                    else "Unknown"
                ),
                "last_message": chat.message,
                "created_at": chat.created_at
            }

    return render_template(
        "inbox.html",
        inbox=list(inbox_data.values()),
        pagination=chats
    )
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





@user.route(
    "/payment-method",
    methods=["GET", "POST"]
)
@login_required
def payment_method():

    # ================= USER =================

    user_id = session.get("user_id")

    # ================= GET OLD METHOD =================

    payment = UserPaymentMethod.query.filter_by(
        user_id=user_id,
        is_default=True
    ).first()

    # ================= SAVE PAYMENT METHOD =================

    if request.method == "POST":

        method = request.form.get("method")
        account_name = request.form.get("account_name")
        account_number = request.form.get("account_number")
        ifsc = request.form.get("ifsc")
        upi_id = request.form.get("upi_id")

        # ================= VALIDATION =================

        if not method:

            flash(
                "Payment method is required",
                "danger"
            )

            return redirect("/user/payment-method")

        # ================= UPI VALIDATION =================

        if method == "upi" and not upi_id:

            flash(
                "UPI ID is required",
                "danger"
            )

            return redirect("/user/payment-method")

        # ================= BANK VALIDATION =================

        if method == "bank":

            if not account_number or not ifsc:

                flash(
                    "Bank account details required",
                    "danger"
                )

                return redirect("/user/payment-method")

        # ================= UPDATE EXISTING =================

        if payment:

            payment.method = method
            payment.account_name = account_name
            payment.account_number = account_number
            payment.ifsc = ifsc
            payment.upi_id = upi_id

        # ================= CREATE NEW =================

        else:

            payment = UserPaymentMethod(

                user_id=user_id,

                method=method,

                account_name=account_name,

                account_number=account_number,

                ifsc=ifsc,

                upi_id=upi_id,

                is_default=True
            )

            db.session.add(payment)

        # ================= SAVE =================

        db.session.commit()

        flash(
            "Payment method updated successfully",
            "success"
        )

        return redirect("/user/wallet")

    # ================= RESPONSE =================

    return render_template(
        "payment_method.html",
        payment=payment
            )

# =====================================================
# REFERRAL
# =====================================================

@user.route("/referral")
@login_required
def referral():

    user_id = session.get("user_id")

    current_user = User.query.get_or_404(user_id)

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 20

    referrals = (
        User.query
        .filter(
            User.referred_by == current_user.id
        )
        .order_by(
            User.id.desc()
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    referral_count = (
        User.query
        .filter(
            User.referred_by == current_user.id
        )
        .count()
    )

    return render_template(
        "user/referral.html",

        referred_users=referrals.items,
        pagination=referrals,

        referral_count=referral_count,
        referral_earnings=0
    )


# =====================================================
# SETTINGS
# =====================================================

@user.route("/settings")
@login_required
def settings():

    return render_template(
        "user/settings.html"
)

@user.route("/my-appointments")
@login_required
def my_appointments():

    page = request.args.get(
        "page",
        default=1,
        type=int
    )

    appointments = (
        Appointment.query
        .options(
            joinedload(Appointment.chamber),
            joinedload(Appointment.doctor)
        )
        .filter_by(
            user_id=session["user_id"]
        )
        .order_by(
            Appointment.id.desc()
        )
        .paginate(
            page=page,
            per_page=20,
            error_out=False
        )
    )

    return render_template(
        "user/my_appointments.html",
        appointments=appointments.items,
        pagination=appointments
    )
