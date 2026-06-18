from extensions import db


class SiteSetting(db.Model):

    __tablename__ = "site_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    running_headline = db.Column(
        db.Text,
        default=""
    )
