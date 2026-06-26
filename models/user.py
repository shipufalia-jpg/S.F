from extensions import db
from datetime import datetime, UTC
from flask_login import UserMixin



class User(UserMixin, db.Model):

    __tablename__ = "user"

    # ======================
    # PRIMARY KEY
    # ======================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================
    # AUTH
    # ======================

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=True,
        index=True
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    # ======================
    # USER INFO
    # ======================

    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    skill = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    area = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    profile_img = db.Column(
        db.Text,
        nullable=True,
        default="/static/default.png"
    )

    # ======================
    # ROLE & STATUS
    # ======================

    role = db.Column(
        db.String(20),
        default="user",
        index=True
    )

    status = db.Column(
        db.String(20),
        default="active",
        index=True
    )

    is_online = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    last_seen = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    socket_id = db.Column(
        db.String(100),
        nullable=True
    )

    # ======================
    # REFERRAL SYSTEM FIXED
    # ======================
    referred_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )

    referrer = db.relationship(
        "User",
        foreign_keys=[referred_by],
        backref=db.backref(
            "referrals",
            remote_side="User.id"
        )
    )
    # ======================
    # CONTROLLER SYSTEM
    # ======================
    controller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )

    controller = db.relationship(
        "User",
        foreign_keys=[controller_id],
        backref=db.backref(
            "controlled_users",
            remote_side="User.id"
        )
    )
    # ======================
    # SOFT DELETE
    # ======================

    is_deleted = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    # ======================
    # AUDIT
    # ======================

    created_by = db.Column(
        db.Integer,
        nullable=True
    )

    updated_by = db.Column(
        db.Integer,
        nullable=True
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    verification_expiry = db.Column(
        db.DateTime,
        index=True
    )

    # ======================
    # TIMESTAMPS
    # ======================

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        index=True
    )

    wallet_balance = db.Column(
        db.Numeric(12,2),
        default=0
    )

    total_earnings = db.Column(
        db.Numeric(12,2),
        default=0
    )

    works = db.relationship(
        "Work",
        back_populates="user",
        lazy="dynamic"
    )

    must_change_password = db.Column(
        db.Boolean,
        default=False
    )

    password_reset_requests = db.relationship(
        "PasswordResetRequest",
        back_populates="user",
        lazy=True
    )
    profile = db.relationship(
        "Profile",
        uselist=False,
        back_populates="user"
    )
    # ======================
    # STRING
    # ======================

    def __repr__(self):
        return f"<User {self.id} - {self.phone}>"
