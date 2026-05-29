from extensions import db
from datetime import datetime


class UserPaymentMethod(db.Model):

    __tablename__ = "user_payment_methods"

    # ================= PRIMARY KEY =================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ================= USER =================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    # ================= PAYMENT INFO =================

    method = db.Column(
        db.String(20),
        nullable=False
    )  # upi / bank / paypal

    account_name = db.Column(
        db.String(100)
    )

    account_number = db.Column(
        db.String(100)
    )

    ifsc = db.Column(
        db.String(50)
    )

    upi_id = db.Column(
        db.String(100)
    )

    # ================= STATUS =================

    is_default = db.Column(
        db.Boolean,
        default=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    # ================= TIMESTAMP =================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ================= RELATIONSHIP =================

    user = db.relationship(
        "User",
        backref=db.backref(
            "payment_methods",
            lazy=True
        )
    )

    # ================= REPRESENT =================

    def __repr__(self):

        return f"<UserPaymentMethod {self.id}>"
