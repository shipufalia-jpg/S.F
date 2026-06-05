from extensions import db


class DoctorGallery(db.Model):

    __tablename__ = "doctor_gallery"

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    image = db.Column(db.String(255), nullable=False)
