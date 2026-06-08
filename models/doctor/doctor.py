from extensions import db
from datetime import datetime


class Doctor(db.Model):

    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)

    # BASIC INFO
    name = db.Column(db.String(150), nullable=False, index=True)
    degree = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(255), index=True)

    hospital = db.Column(db.String(255))
    experience = db.Column(db.String(100))
    about = db.Column(db.Text)

    # MEDIA
    profile_photo = db.Column(db.String(255))
    cover_photo = db.Column(db.String(255))

    # STATUS
    verified = db.Column(db.Boolean, default=False, index=True)

    # ANALYTICS
    views = db.Column(db.Integer, default=0)

    # TIMESTAMP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONS
    chamber_id = db.Column(
        db.Integer,
        db.ForeignKey("chambers.id"),
        nullable=False,
        index=True
    )

    ratings = db.relationship(
        "DoctorRating",
        backref="doctor",
        lazy=True,
        cascade="all, delete-orphan"
    )

    gallery = db.relationship(
        "DoctorGallery",
        backref="doctor",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Doctor {self.name}>"
