from datetime import datetime
from extensions import db


class WorkApplication(db.Model):
    __tablename__ = "work_applications"

    # ================= PRIMARY KEY =================
    id = db.Column(db.Integer, primary_key=True)

    # ================= RELATIONS =================
    work_id = db.Column(
        db.Integer,
        db.ForeignKey('work.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ================= USER SNAPSHOT =================
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)

    # ================= APPLICATION STATUS =================
    status = db.Column(
        db.Enum(
            "applied",
            "approved",
            "rejected",
            "cancelled",
            name="app_status"
        ),
        default="applied",
        nullable=False,
        index=True
    )

    # ================= EXTRA DETAILS =================
    message = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    expected_salary = db.Column(db.String(50))

    # ================= TRACKING FLAGS =================
    is_seen = db.Column(db.Boolean, default=False)
    is_shortlisted = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    # ================= META =================
    applied_ip = db.Column(db.String(45))

    # ================= TIMESTAMPS =================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    edited_at = db.Column(db.DateTime)

    # ================= CONSTRAINTS =================
    __table_args__ = (
        db.UniqueConstraint(
            'work_id',
            'user_id',
            name='unique_work_application'
        ),
  )
