from extensions import db
from datetime import datetime
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
        nullable=True
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
        db.DateTime,
        default=datetime.utcnow
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
        remote_side=[id],
        foreign_keys=[referred_by],
        backref="referrals"
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
        remote_side=[id],
        foreign_keys=[controller_id],
        backref="controlled_users"
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

    # ======================
    # TIMESTAMPS
    # ======================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    works = db.relationship(
    "Work",
    back_populates="user",
    lazy=True
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    wallet_balance = db.Column(db.Float, default=0.0)
    total_earnings = db.Column(db.Float, default=0.0)
    # ======================
    # STRING
    # ======================

    def __repr__(self):
        return f"<User {self.id} - {self.phone}>"
