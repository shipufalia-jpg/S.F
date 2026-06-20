from extensions import db
from datetime import datetime
from sqlalchemy.sql import func


class Chat(db.Model):
    __tablename__ = "chat"
    __table_args__ = (
    db.Index(
        "idx_chat_users",
        "sender_id",
        "receiver_id"
    ),
    db.Index(
        "idx_chat_created",
        "created_at"
    ),
 )

    # 🆔 PRIMARY KEY
    id = db.Column(db.Integer, primary_key=True)

    # 👤 USERS
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )

    # 💬 MESSAGE
    message = db.Column(db.Text, nullable=False)

    # 📊 READ STATUS
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)

    # 🚫 MODERATION SYSTEM
    is_blocked = db.Column(db.Boolean, default=False, index=True)
    blocked_by = db.Column(db.Integer, nullable=True, index=True)
    blocked_at = db.Column(db.DateTime, nullable=True)

    # 🗑 SOFT DELETE
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    deleted_by = db.Column(db.Integer, nullable=True, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 🔒 REPORT SYSTEM
    is_reported = db.Column(db.Boolean, default=False, index=True)
    report_reason = db.Column(db.Text, nullable=True)

    # ⌨️ TYPING INDICATOR
    is_typing = db.Column(db.Boolean, default=False, index=True)
    typing_at = db.Column(db.DateTime, nullable=True)

    # 🕒 TIMESTAMPS
    created_at = db.Column(
        db.DateTime,
        default=func.now(),
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 🔁 RELATIONSHIP
    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        lazy="select"
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        lazy="select"
    )

    # 📌 HELPERS
    def mark_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()

    def set_typing(self, status=True):
        self.is_typing = status
        self.typing_at = datetime.utcnow()
