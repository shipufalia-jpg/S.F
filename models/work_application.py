from datetime import datetime
from extensions import db


class WorkApplication(db.Model):
    __tablename__ = "work_applications"

    # =====================================================
    # PRIMARY KEY
    # =====================================================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # RELATIONS
    # =====================================================
    user = db.relationship(
        "User",
        backref=db.backref(
            "applications",
            lazy="dynamic"
        ),
        lazy="select"
    )

    work = db.relationship(
        "Work",
        backref=db.backref(
            "applications",
            lazy="dynamic"
        ),
        lazy="select"
    )

    # =====================================================
    # USER SNAPSHOT
    # =====================================================
    name = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    address = db.Column(
        db.Text
    )

    # =====================================================
    # APPLICATION STATUS
    # =====================================================
    status = db.Column(
        db.Enum(
            "applied",
            "approved",
            "rejected",
            "cancelled",
            name="app_status"
        ),
        nullable=False,
        default="applied",
        index=True
    )

    # =====================================================
    # EXTRA DETAILS
    # =====================================================
    message = db.Column(
        db.Text
    )

    experience_years = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    expected_salary = db.Column(
        db.Integer
    )

    # =====================================================
    # TRACKING FLAGS
    # =====================================================
    is_seen = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    is_shortlisted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # =====================================================
    # META
    # =====================================================
    applied_ip = db.Column(
        db.String(50)
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )

    edited_at = db.Column(
        db.DateTime
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    user = db.relationship(
        "User",
        backref=db.backref(
            "applications",
            lazy="dynamic"
        ),
        lazy="joined"
    )

    work = db.relationship(
        "Work",
        backref=db.backref(
            "applications",
            lazy="dynamic"
        ),
        lazy="joined"
    )

    # =====================================================
    # CONSTRAINTS & INDEXES
    # =====================================================
    __table_args__ = (

        # Prevent duplicate applications
        db.UniqueConstraint(
            "work_id",
            "user_id",
            name="unique_work_application"
        ),

        # Fast user application lookup
        db.Index(
            "idx_application_user_deleted",
            "user_id",
            "is_deleted"
        ),

        # Fast status analytics
        db.Index(
            "idx_application_status_created",
            "status",
            "created_at"
        ),

        # Fast work lookup
        db.Index(
            "idx_application_work_status",
            "work_id",
            "status"
        ),
    )

    # =====================================================
    # HELPERS
    # =====================================================
    def soft_delete(self):
        self.is_deleted = True
        self.edited_at = datetime.utcnow()

    def mark_seen(self):
        self.is_seen = True
        self.edited_at = datetime.utcnow()

    def shortlist(self):
        self.is_shortlisted = True
        self.edited_at = datetime.utcnow()

    def __repr__(self):
        return (
            f"<WorkApplication "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"work_id={self.work_id} "
            f"status={self.status}>"
        )
