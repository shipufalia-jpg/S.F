from extensions import db


class Chamber(db.Model):

    __tablename__ = "doctor_chambers"

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    chamber_name = db.Column(db.String(255), nullable=False)

    area = db.Column(db.String(150), nullable=False, index=True)

    address = db.Column(db.Text)

    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))

    day = db.Column(db.String(100))
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
