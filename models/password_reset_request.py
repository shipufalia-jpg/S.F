from extensions import db
from datetime import datetime

class PasswordResetRequest(db.Model):

__tablename__ = "password_reset_requests"

id = db.Column(
    db.Integer,
    primary_key=True
)

# Request User
user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=False,
    index=True
)

# Phone Snapshot
phone = db.Column(
    db.String(20),
    nullable=False,
    index=True
)

# pending | approved | completed | rejected
status = db.Column(
    db.String(20),
    nullable=False,
    default="pending",
    index=True
)

# Admin Note
admin_note = db.Column(
    db.Text,
    nullable=True
)

# Who approved/rejected
handled_by = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=True
)

# Created Time
created_at = db.Column(
    db.DateTime,
    nullable=False,
    default=datetime.utcnow,
    index=True
)

# Process Time
processed_at = db.Column(
    db.DateTime,
    nullable=True
)

# Relationship
user = db.relationship(
    "User",
    foreign_keys=[user_id],
    lazy="joined"
)

handler = db.relationship(
    "User",
    foreign_keys=[handled_by],
    lazy="joined"
)

def approve(self, admin_id):

    self.status = "approved"
    self.handled_by = admin_id
    self.processed_at = datetime.utcnow()

def reject(self, admin_id, note=None):

    self.status = "rejected"
    self.handled_by = admin_id
    self.admin_note = note
    self.processed_at = datetime.utcnow()

def complete(self, admin_id):

    self.status = "completed"
    self.handled_by = admin_id
    self.processed_at = datetime.utcnow()

def __repr__(self):

    return (
        f"<PasswordResetRequest "
        f"id={self.id} "
        f"user_id={self.user_id} "
        f"status={self.status}>"
)
