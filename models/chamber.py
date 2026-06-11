from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Chamber(db.Model):

    __tablename__ = "chambers"

    id = db.Column(db.Integer, primary_key=True)

    # =========================
    # BASIC INFO
    # =========================
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))

    status = db.Column(db.String(20), default="active", index=True)

    # =========================
    # ADMIN RELATIONS
    # =========================
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    controller_admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    super_admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # =========================
    # TIMESTAMPS
    # =========================
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # RELATIONSHIPS
    # =========================

    # Doctors
    doctors = db.relationship(
        "Doctor",
        back_populates="chamber",
        cascade="all, delete-orphan",
        lazy=True
    )

    # Profile (1-to-1)
    profile = db.relationship(
        "ChamberProfile",
        back_populates="chamber",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # =========================
    # AUTH
    # =========================

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
