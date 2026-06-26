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
        db.ForeignKey("work.id"),
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
    # ACTION BY
    # =========================================

    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )

    rejected_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )

    blocked_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )

    deleted_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
        index=True
    )
    

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
    approved_user = db.relationship(
        "User",
        foreign_keys=[approved_by],
        backref="approved_bookings",
        lazy=True
    )

    rejected_user = db.relationship(
        "User",
        foreign_keys=[rejected_by],
        backref="rejected_bookings",
        lazy=True
    )

    blocked_user = db.relationship(
        "User",
        foreign_keys=[blocked_by],
        backref="blocked_bookings",
        lazy=True
    )

    deleted_user = db.relationship(
        "User",
        foreign_keys=[deleted_by],
        backref="deleted_bookings",
        lazy=True
    )

    # =========================================
    # STRING
    # =========================================
    def __repr__(self):
        return f"<Booking {self.id}>"
        
