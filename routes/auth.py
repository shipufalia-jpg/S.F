from flask import (
    Blueprint,
    request,
    redirect,
    session,
    render_template,
    url_for,
    flash
)
from functools import wraps

from models.user import User
from models.profile import Profile

from extensions import db

from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from utils.control import assign_control
from models.password_reset_request import PasswordResetRequest
import re




auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =====================================================
# PASSWORD VALIDATION
# =====================================================

def validate_password(password):

    if len(password) < 8:
        return "Password must be at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"\d", password):
        return "Password must contain at least one number."

    if not re.search(r"[@#&!$%^*()_+=\-{}\[\]:;,.?/]", password):
        return "Password must contain at least one special symbol."

    return None


# =====================================================
# LOGIN REQUIRED
# =====================================================

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return wrapper


# =====================================================
# SIGNUP
# =====================================================

@auth.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    # =====================
    # FORM DATA
    # =====================

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    password_raw = request.form.get("password", "")
    role = request.form.get("role", "user").strip().lower()

    # =====================
    # ROLE VALIDATION
    # =====================

    allowed_roles = ["user", "admin", "super_admin"]

    if role not in allowed_roles:
        role = "user"

    # =====================
    # REQUIRED CHECK
    # =====================

    if not name or not phone or not password_raw:
        return "All fields required"

    # =====================
    # PHONE VALIDATION
    # =====================

    if not re.fullmatch(r"\d{10,15}", phone):
        return "Invalid phone number"

    # =====================
    # PASSWORD VALIDATION
    # =====================

    password_error = validate_password(password_raw)

    if password_error:
        return password_error

    # =====================
    # DUPLICATE PHONE
    # =====================

    existing = User.query.filter_by(phone=phone).first()

    if existing:
        return "Phone already registered"

    # =====================
    # HASH PASSWORD
    # =====================

    password_hash = generate_password_hash(
        password_raw,
        method="pbkdf2:sha256",
        salt_length=16
    )

    # =====================
    # REFERRAL
    # =====================

    ref_id = request.form.get("ref_id")

    referrer = None

    if ref_id and str(ref_id).isdigit():
        referrer = db.session.get(User, int(ref_id))

    # =====================
    # STATUS
    # =====================

    status = "active" if role == "user" else "pending"

    # =====================
    # CREATE USER
    # =====================

    user = User(
        name=name,
        phone=phone,
        password=password_hash,
        role=role,
        status=status
    )

    if referrer:
        user.referred_by = referrer.id

    # =====================
    # CONTROL SYSTEM
    # =====================

    assign_control(user, referrer)

    # =====================
    # OWNER CONTROL
    # =====================

    if not referrer:

        owner = User.query.filter_by(
            role="owner"
        ).first()

        if owner:
            user.controller_id = owner.id

    try:

        db.session.add(user)
        db.session.flush()

        profile = Profile(
            user_id=user.id,
            name=name
        )

        db.session.add(profile)

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        return f"Signup error: {str(e)}"

    if role == "user":
        return redirect(url_for("auth.login"))

    return "Signup submitted. Waiting for owner approval."


# =====================================================
# LOGIN
# =====================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")

    if not phone or not password:
        return "All fields required"

    user = User.query.filter_by(phone=phone).first()

    if not user:
        return "Invalid phone or password"

    if user.status == "blocked":
        return "Account blocked"

    if user.status != "active":
        return "Account not approved yet"

    if not check_password_hash(
        user.password,
        password
    ):
        return "Invalid phone or password"

    try:

        user.is_online = True
        user.last_seen = datetime.utcnow()

        db.session.commit()

    except Exception:
        db.session.rollback()

    # =====================
    # SESSION SECURITY
    # =====================

    session.clear()

    session.permanent = True

    session["user_id"] = user.id
    session["role"] = (user.role or "").lower().strip()

    role = session["role"]

    # =====================
    # ROLE REDIRECT
    # =====================

    if role == "owner":
        return redirect("/owner/dashboard")

    elif role == "super_admin":
        return redirect("/super/")

    elif role == "admin":
        return redirect("/admin/")

    return redirect("/user/dashboard")


@auth.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "GET":
        return render_template(
            "forgot_password.html"
        )

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    # ==========================
    # VALIDATION
    # ==========================

    if not phone:
        flash(
            "Phone number is required.",
            "danger"
        )
        return redirect(
            url_for(
                "auth.forgot_password"
            )
        )

    if not re.fullmatch(
        r"\d{10,15}",
        phone
    ):
        flash(
            "Invalid phone number.",
            "danger"
        )
        return redirect(
            url_for(
                "auth.forgot_password"
            )
        )

    try:

        user = User.query.filter_by(
            phone=phone
        ).first()

        if not user:

            flash(
                "If the account exists, a reset request has been submitted.",
                "success"
            )

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        pending = (
            PasswordResetRequest.query
            .filter_by(
                user_id=user.id,
                status="pending"
            )
            .first()
        )

        if pending:

            flash(
                "A password reset request is already pending.",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        req = PasswordResetRequest(
            user_id=user.id,
            phone=user.phone,
            status="pending"
        )

        db.session.add(req)
        db.session.commit()

        flash(
            "Password reset request submitted successfully.",
            "success"
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )

    except Exception as e:

        db.session.rollback()

        print(
            "Forgot Password Error:",
            e
        )

        flash(
            "Something went wrong. Please try again.",
            "danger"
        )

        return redirect(
            url_for(
                "auth.forgot_password"
            )
        )

@auth.route(
"/change-password",
methods=["GET", "POST"]
)
@login_required
def change_password():

user = db.session.get(
    User,
    session["user_id"]
)

if not user:
    session.clear()
    return redirect(
        url_for("auth.login")
    )

if request.method == "GET":

    return render_template(
        "change_password.html"
    )

password = (
    request.form.get(
        "password",
        ""
    ).strip()
)

error = validate_password(
    password
)

if error:

    flash(
        error,
        "danger"
    )

    return redirect(
        url_for(
            "auth.change_password"
        )
    )

try:

    user.password = generate_password_hash(
        password,
        method="pbkdf2:sha256",
        salt_length=16
    )

    user.must_change_password = False

    db.session.commit()

    flash(
        "Password changed successfully.",
        "success"
    )

    return redirect(
        "/user/dashboard"
    )

except Exception as e:

    db.session.rollback()

    print(
        "Change Password Error:",
        e
    )

    flash(
        "Something went wrong.",
        "danger"
    )

    return redirect(
        url_for(
            "auth.change_password"
        )
    )
# =====================================================
# LOGOUT
# =====================================================

@auth.route("/logout")
def logout():

    try:

        user_id = session.get("user_id")

        if user_id:

            user = db.session.get(User, user_id)

            if user:
                user.is_online = False
                user.last_seen = datetime.utcnow()

                db.session.commit()

    except Exception:
        db.session.rollback()

    session.clear()

    return redirect(url_for("auth.login"))
