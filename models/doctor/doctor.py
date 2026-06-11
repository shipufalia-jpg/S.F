from extensions import db
from datetime import datetime


class Doctor(db.Model):

    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)

    # =========================
    # BASIC INFO
    # =========================
    name = db.Column(db.String(150), nullable=False, index=True)
    degree = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(255), index=True)

    hospital = db.Column(db.String(255))
    experience = db.Column(db.String(100))
    about = db.Column(db.Text)

    # =========================
    # MEDIA (Cloudinary supported)
    # =========================
    profile_photo = db.Column(db.String(255))
    cover_photo = db.Column(db.String(255))

    # =========================
    # STATUS
    # =========================
    verified = db.Column(db.Boolean, default=False, index=True)

    # =========================
    # ANALYTICS
    # =========================
    views = db.Column(db.Integer, default=0)

    # =========================
    # TIMESTAMP
    # =========================
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # RELATIONSHIP (IMPORTANT FIX)
    # =========================
    chamber_id = db.Column(
        db.Integer,
        db.ForeignKey("chambers.id"),
        nullable=False,
        index=True
    )

    chamber = db.relationship(
        "Chamber",
        back_populates="doctors"
    )

    # =========================
    # RATINGS
    # =========================
    ratings = db.relationship(
        "DoctorRating",
        backref="doctor",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # =========================
    # DEBUG
    # =========================
    def __repr__(self):
        return f"<Doctor {self.name}>"
