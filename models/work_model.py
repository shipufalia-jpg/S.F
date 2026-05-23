from datetime import datetime
from extensions import db


class Work(db.Model):

    __tablename__ = "works"

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

    # ================= EXTRA WORK INFO =================
    workers = db.Column(
        db.String(100)
    )

    salary = db.Column(
        db.String(100)
    )

    date = db.Column(
        db.String(100)
    )

    time = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(20)
    )

    # ================= USER =================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )

    # ================= RELATIONSHIP =================
    user = db.relationship(
        'User',
        back_populates='works'
    )

    # ================= STATUS =================
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    is_active = db.Column(
        db.Boolean,
        default=False
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    edit_count = db.Column(
        db.Integer,
        default=0
    )

    # ================= OWNER ACTION =================
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
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ================= STRING =================
    def __repr__(self):

        return (
            f"<Work "
            f"{self.id} | "
            f"{self.title} | "
            f"{self.status}>"
    )
