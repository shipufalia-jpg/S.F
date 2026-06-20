from flask import (
    Blueprint,
    session,
    redirect,
    render_template,
    flash
)
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import joinedload
from datetime import datetime
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
    medias = LiveMedia.query.filter(
        LiveMedia.is_active.is_(True),
        LiveMedia.is_deleted.is_(False),
        LiveMedia.is_approved.is_(True),
        (
            (LiveMedia.target_role == "all") |
            (LiveMedia.target_role == role)
        ),
        (
            (LiveMedia.start_time == None) |
            (LiveMedia.start_time <= now)
        ),
        (
            (LiveMedia.end_time == None) |
            (LiveMedia.end_time >= now)
        )
    ).order_by(
        LiveMedia.force_show.desc(),
        LiveMedia.is_featured.desc(),
        LiveMedia.display_order.asc(),
        LiveMedia.id.desc()
    ).limit(50).all()
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

    current_user_data = db.session.get(
        User,
        user_id
    )

    if not current_user_data:
        session.clear()
        return redirect('/auth/login')

    setting = SiteSetting.query.first()

    # ================= PAGINATION =================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 20

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
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    
    # ================= USERS =================

    profiles = (
        Profile.query
        .options(
            joinedload(Profile.user)
        )
        .filter(
            Profile.user_id != user_id
        )
        .order_by(Profile.id.desc())
        .paginate(
            page=page,
            per_page=20,
            error_out=False
        )
    )
    # ================= STATS =================

    total_works = db.session.query(
        db.func.count(Work.id)
    ).filter(
        Work.status == "approved"
    ).scalar()

    total_profiles = db.session.query(
        db.func.count(Profile.id)
    ).scalar()

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
# 👤 PUBLIC PROFILE VIEW
# =================================================
# =================================================
# 💬 CHAT SYSTEM
# =================================================

@user.route("/chat/<int:user_id>")
@login_required
def chat(user_id):

    current_user_id = session.get("user_id")

    receiver = User.query.get_or_404(user_id)

    page = request.args.get(
        "page",
        1,
        type=int
    )

    messages = (
        Chat.query
        .filter(
            (
                (Chat.sender_id == current_user_id) &
                (Chat.receiver_id == user_id)
            ) |
            (
                (Chat.sender_id == user_id) &
                (Chat.receiver_id == current_user_id)
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
        messages=messages.items,
        pagination=messages,
        current_user_id=current_user_id
    )

@user.route("/inbox")
@login_required
def inbox():

    user_id = session.get("user_id")

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
            per_page=20,
            error_out=False
        )
    )

    inbox_data = {}

    for c in chats.items:

        other = (
            c.receiver_id
            if c.sender_id == user_id
            else c.sender_id
        )

        if other not in inbox_data:
            inbox_data[other] = {
                "user_id": other,
                "last_message": c.message
            }

    return render_template(
        "inbox.html",
        inbox=inbox_data.values(),
        pagination=chats
            )

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
        per_page=20,
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

@user.route("/referral")
@login_required
def referral():

    current_user = User.query.get(
        session["user_id"]
    )

    referred_users = User.query.filter_by(
        referred_by=current_user.id
    ).order_by(
        User.id.desc()
    ).all()

    return render_template(
    "user/referral.html",
    referred_users=referred_users,
    referral_count=len(referred_users),
    referral_earnings=0
    )

@user.route("/settings")
@login_required
def settings():
    return render_template("user/settings.html")


@user.route("/my-appointments")
def my_appointments():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/auth/login")

    page = request.args.get(
        "page",
        1,
        type=int
    )

    appointments = Appointment.query.options(
        joinedload(Appointment.chamber),
        joinedload(Appointment.doctor)
    ).filter(
        Appointment.user_id == user_id
    ).order_by(
        Appointment.id.desc()
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template(
        "user/my_appointments.html",
        appointments=appointments.items,
        pagination=appointments
    )

