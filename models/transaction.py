from extensions import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    # ================= UNIQUE ID =================
    transaction_id = db.Column(
        db.String(64),
        unique=True,
        index=True,
        nullable=False
    )

    # ================= USER =================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        index=True,
        nullable=False
    )

    # ================= AMOUNT =================
    amount = db.Column(
        db.Float,
        nullable=False
    )

    # ================= TYPE =================
    type = db.Column(
        db.String(30),
        nullable=False
    )
    # credit / debit / transfer_in / transfer_out / withdraw / referral

    # ================= STATUS =================
    status = db.Column(
        db.String(20),
        default="success",
        index=True
    )
    # pending / success / failed / cancelled

    # ================= REASON =================
    reason = db.Column(
        db.String(255),
        nullable=True
    )

    # ================= BALANCE SNAPSHOT =================
    balance_before = db.Column(
        db.Float,
        default=0
    )

    balance_after = db.Column(
        db.Float,
        default=0
    )

    # ================= RELATED REF / WITHDRAW =================
    reference_id = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )
    # withdraw_request_id / referral_id etc

    reference_type = db.Column(
        db.String(50),
        nullable=True
    )
    # withdraw / referral / manual / system

    # ================= ADMIN CONTROL =================
    processed_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
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

    # ================= RELATIONSHIP =================
    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref="transactions"
  )
