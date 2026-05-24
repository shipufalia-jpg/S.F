from flask import Blueprint, request, redirect, session, render_template, url_for
from functools import wraps

from models.user import User
from models.profile import Profile
from extensions import db
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from utils.control import assign_control   # ✅ single import only

auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =========================================================
# LOGIN REQUIRED
# =========================================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return wrapper


# =========================================================
# SIGNUP
# =========================================================
@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    # ================= SHOW PAGE =================
    if request.method == 'GET':
        return render_template('signup.html')

    # ================= FORM DATA =================
    name = request.form.get('name')
    phone = request.form.get('phone')
    password_raw = request.form.get('password')
    role = request.form.get('role')

    # ================= ROLE VALIDATION =================
    if role not in ["user", "admin", "super_admin"]:
        role = "user"

    # ================= VALIDATION =================
    if not all([name, phone, password_raw]):
        return "All fields required"

    # ================= DUPLICATE CHECK =================
    existing = User.query.filter_by(phone=phone).first()
    if existing:
        return "Phone already registered"

    # ================= PASSWORD HASH =================
    password = generate_password_hash(password_raw)

    # ================= REFERRAL =================
    ref_id = request.form.get('ref_id')
    referrer = User.query.get(ref_id) if ref_id else None

    # ================= STATUS LOGIC =================
    # user → auto active
    # admin / super_admin → owner approval
    if role == "user":
        status = "active"
    else:
        status = "pending"

    # ================= CREATE USER =================
    user = User(
        name=name,
        phone=phone,
        password=password,
        role=role,
        status=status
    )

    # ================= CONTROL SYSTEM =================
    # referral hierarchy logic
    assign_control(user, referrer)

    # ================= OWNER DEFAULT CONTROL =================
    # যদি referral না থাকে → owner control
    if not referrer:
        owner = User.query.filter_by(role="owner").first()
        if owner:
            user.controller_id = owner.id

    try:
        # ================= SAVE USER =================
        db.session.add(user)
        db.session.flush()

        # ================= PROFILE CREATE =================
        profile = Profile(
            user_id=user.id,
            name=name
        )

        db.session.add(profile)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return f"Signup error: {e}"

    # ================= RESPONSE =================
    if role == "user":
        return redirect(url_for('auth.login'))

    return "Signup submitted. Waiting for owner approval."


# =========================================================
# LOGIN
# =========================================================
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    phone = request.form.get('phone')
    password = request.form.get('password')

    # ================= VALIDATION =================
    if not phone or not password:
        return "All fields required"

    # ================= FIND USER =================
    user = User.query.filter_by(phone=phone).first()

    if not user:
        return "User not found"

    # ================= STATUS CHECK =================
    if user.status == "blocked":
        return "Account blocked"

    if user.status != "active":
        return "Account not approved yet"

    # ================= PASSWORD CHECK =================
    if not check_password_hash(user.password, password):
        return "Wrong password"

    # ================= UPDATE ONLINE STATUS =================
    user.is_online = True
    user.last_seen = datetime.utcnow()

    db.session.commit()

    # ================= SESSION =================
    session.clear()

    session["user_id"] = user.id
    session["role"] = (user.role or "").lower().strip()

    role = session["role"]

    # ================= ROLE REDIRECT =================

    # OWNER
    if role == "owner":
        return redirect("/owner/dashboard")

    # SUPER ADMIN
    elif role == "super_admin":
        return redirect("/super/")

    # ADMIN
    elif role == "admin":
        return redirect("/admin/")

    # USER
    return redirect("/user/dashboard")
    
# =========================================================
# LOGOUT
# =========================================================
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
    
