from extensions import db
from datetime import datetime


class WithdrawRequest(db.Model):

    __tablename__ = "withdraw_requests"

    id = db.Column(db.Integer, primary_key=True)

    # ================= USER =================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    # ================= AMOUNT =================

    amount = db.Column(
        db.Float,
        nullable=False
    )

    # ================= STATUS =================

    status = db.Column(
        db.String(20),
        default="pending",
        index=True
    )
    # pending / approved / rejected

    # ================= PAYMENT INFO =================

    payment_method = db.Column(
        db.String(50),
        default="manual"
    )
    # bank / upi / bkash / nagad etc

    payment_account = db.Column(
        db.String(100),
        nullable=True
    )

    # ================= PAYMENT CONTROL =================

    payment_status = db.Column(
        db.String(20),
        default="unpaid",
        index=True
    )
    # unpaid / paid

    paid_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    paid_at = db.Column(
        db.DateTime,
        nullable=True
    )

    utr_number = db.Column(
        db.String(100),
        nullable=True
    )

    admin_note = db.Column(
        db.Text,
        nullable=True
    )

    # ================= ADMIN CONTROL =================

    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    rejected_reason = db.Column(
        db.String(255),
        nullable=True
    )

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

    processed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ================= RELATIONSHIP =================

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref="withdraw_requests"
    )

    approver = db.relationship(
        "User",
        foreign_keys=[approved_by]
    )

    payer = db.relationship(
        "User",
        foreign_keys=[paid_by]
    )
