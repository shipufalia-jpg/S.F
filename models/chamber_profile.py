from extensions import db
from datetime import datetime


class ChamberProfile(db.Model):

    __tablename__ = "chamber_profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    chamber_id = db.Column(
        db.Integer,
        db.ForeignKey("chambers.id"),
        unique=True,
        nullable=False,
        index=True
    )

    chamber = db.relationship(
        "Chamber",
        backref=db.backref(
        "profile",
        uselist=False
    )
)
    

    # =========================
    # BASIC INFO
    # =========================

    chamber_name = db.Column(
        db.String(255),
        nullable=False
    )

    phone = db.Column(
        db.String(20)
    )

    whatsapp = db.Column(
        db.String(20)
    )

    email = db.Column(
        db.String(120)
    )

    website = db.Column(
        db.String(255)
    )

    # =========================
    # LOCATION
    # =========================

    area = db.Column(
        db.String(150),
        index=True
    )

    address = db.Column(
        db.Text
    )

    # =========================
    # MEDIA
    # =========================

    profile_image = db.Column(
        db.String(255)
    )

    cover_image = db.Column(
        db.String(255)
    )

    logo = db.Column(
        db.String(255)
    )

    # =========================
    # DETAILS
    # =========================

    description = db.Column(
        db.Text
    )

    # =========================
    # STATUS
    # =========================

    verified = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    status = db.Column(
        db.String(20),
        default="active",
        index=True
    )

    # =========================
    # ANALYTICS
    # =========================

    views = db.Column(
        db.Integer,
        default=0
    )

    rating = db.Column(
        db.Float,
        default=0
    )

    total_reviews = db.Column(
        db.Integer,
        default=0
    )

    # =========================
    # TIMESTAMPS
    # =========================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
  )
