from extensions import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    # কে action করলো
    actor_id = db.Column(db.Integer, index=True, nullable=False)

    # কাকে করা হলো
    target_id = db.Column(db.Integer, index=True)

    # action type
    action = db.Column(db.String(50), index=True, nullable=False)

    # role (admin / super_admin)
    role = db.Column(db.String(20), index=True)

    # extra info (JSON format)
    meta = db.Column(db.JSON, nullable=True)

    # IP address
    ip_address = db.Column(db.String(45))

    # timestamp
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
  )
