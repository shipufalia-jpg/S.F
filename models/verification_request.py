from extensions import db
from datetime import datetime


class VerificationRequest(db.Model):

    __tablename__ = "verification_requests"

    # ======================
    # PRIMARY KEY
    # ======================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================
    # USER
    # ======================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    # ======================
    # VERIFICATION PLAN
    # ======================

    plan_months = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    amount = db.Column(
        db.Float,
        nullable=False,
        default=100
    )

    # ======================
    # PAYMENT
    # ======================

    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )
    # pending
    # paid
    # failed

    transaction_id = db.Column(
        db.String(100)
    )

    # ======================
    # REQUEST STATUS
    # ======================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )
    # pending
    # approved
    # rejected

    rejection_reason = db.Column(
        db.Text
    )

    # ======================
    # DOCUMENTS
    # ======================

    document_url = db.Column(
        db.String(500)
    )

    # ======================
    # TIMESTAMPS
    # ======================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    reviewed_at = db.Column(
        db.DateTime
    )

    # ======================
    # RELATIONSHIP
    # ======================

    user = db.relationship(
        "User",
        backref="verification_requests"
    )

    # ======================
    # REPRESENTATION
    # ======================

    def __repr__(self):
        return (
            f"<VerificationRequest "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"status={self.status}>"
        )
