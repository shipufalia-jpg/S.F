from datetime import datetime, UTC
from extensions import db


class Work(db.Model):

    __tablename__ = "work"

    __table_args__ = (
        db.Index("idx_work_status", "status"),
        db.Index("idx_work_created", "created_at"),
        db.Index("idx_work_user", "user_id"),
    )

    # ================= PRIMARY KEY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ================= WORK INFO =================

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    mobile = db.Column(
        db.String(15),
        nullable=True
    )

    workers = db.Column(
        db.String(100),
        nullable=True
    )

    salary = db.Column(
        db.String(100),
        nullable=True
    )

    date = db.Column(
        db.String(100),
        nullable=True
    )

    time = db.Column(
        db.String(100),
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    # ================= USER =================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        back_populates="works",
        lazy="joined"
    )

    # ================= STATUS =================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
        index=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    is_deleted = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    edit_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # ================= ADMIN ACTION =================

    approved_by = db.Column(
        db.Integer,
        nullable=True
    )

    rejected_by = db.Column(
        db.Integer,
        nullable=True
    )

    edited_by = db.Column(
        db.Integer,
        nullable=True
    )

    # ================= TIMESTAMP =================

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ================= STRING =================

    def __repr__(self):
        return f"<Work {self.id} | {self.title} | {self.status}>"
