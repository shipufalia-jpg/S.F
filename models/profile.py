from extensions import db
from datetime import datetime


class Profile(db.Model):

    __tablename__ = "profile"

    # ================= PRIMARY KEY =================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ================= USER LINK =================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "profile",
            uselist=False
        )
    )

    # ================= BASIC INFO =================
    name = db.Column(db.String(100))

    address = db.Column(db.String(200))

    age = db.Column(db.Integer)

    education = db.Column(db.String(100))

    area = db.Column(db.String(100))

    gender = db.Column(db.String(20))

    religion = db.Column(db.String(50))

    country = db.Column(db.String(50))

    # ================= WORK INFO =================
    work_desc = db.Column(db.Text)

    # ================= IMAGES =================
    profile_img = db.Column(db.String(300))

    cover_img = db.Column(db.String(300))

    # JSON string
    gallery = db.Column(db.Text)

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

    # ================= DEBUG =================
    def __repr__(self):

        return f"<Profile {self.name}>"
        