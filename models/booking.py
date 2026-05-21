from extensions import db
from datetime import datetime


class Booking(db.Model):

    __tablename__ = "bookings"

    # =========================================
    # PRIMARY KEY
    # =========================================
    id = db.Column(db.Integer, primary_key=True)

    # =========================================
    # USERS
    # =========================================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    # =========================================
    # WORK
    # =========================================
    work_id = db.Column(
        db.Integer,
        db.ForeignKey("works.id"),
        nullable=False,
        index=True
    )

    # =========================================
    # BOOKING DETAILS
    # =========================================
    booking_date = db.Column(db.String(50), nullable=True)
    booking_time = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    price = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )

    # =========================================
    # STATUS
    # =========================================
    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False,
        index=True
    )
    # pending / accepted / rejected / completed / cancelled

    payment_status = db.Column(
        db.String(20),
        default="unpaid",
        nullable=False
    )
    # unpaid / paid

    # =========================================
    # SOFT DELETE SYSTEM (SAFE)
    # =========================================

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # =========================================
    # TIMESTAMPS
    # =========================================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =========================================
    # RELATIONSHIPS
    # =========================================
    work = db.relationship(
        "Work",
        backref="bookings",
        lazy=True
    )

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref="user_bookings",
        lazy=True
    )

    owner = db.relationship(
        "User",
        foreign_keys=[owner_id],
        backref="owner_bookings",
        lazy=True
    )

    # =========================================
    # STRING
    # =========================================
    def __repr__(self):
        return f"<Booking {self.id}>"
        