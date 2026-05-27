# models/live_media.py

from extensions import db
from datetime import datetime


class LiveMedia(db.Model):

    __tablename__ = "live_media"

    # =====================================================
    # PRIMARY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # BASIC INFO
    # =====================================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    media_type = db.Column(
        db.String(20),
        nullable=False
    )
    # video / banner / audio / popup / live_tv

    category = db.Column(
        db.String(50),
        default="general"
    )

    # =====================================================
    # FILES
    # =====================================================

    file_url = db.Column(
        db.Text,
        nullable=False
    )

    thumbnail = db.Column(
        db.Text
    )

    preview_image = db.Column(
        db.Text
    )

    original_filename = db.Column(
        db.String(255)
    )

    file_size = db.Column(
        db.BigInteger,
        default=0
    )

    mime_type = db.Column(
        db.String(100)
    )

    duration = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # DISPLAY CONTROLS
    # =====================================================

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    force_show = db.Column(
        db.Boolean,
        default=False
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    auto_play = db.Column(
        db.Boolean,
        default=False
    )

    allow_skip = db.Column(
        db.Boolean,
        default=True
    )

    show_popup = db.Column(
        db.Boolean,
        default=False
    )

    popup_delay = db.Column(
        db.Integer,
        default=0
    )

    display_order = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # LIVE TV SYSTEM
    # =====================================================

    is_live = db.Column(
        db.Boolean,
        default=False
    )

    stream_url = db.Column(
        db.Text
    )

    live_status = db.Column(
        db.String(20),
        default="offline"
    )
    # offline / live / scheduled

    # =====================================================
    # PLAYER CONTROLS
    # =====================================================

    allow_fullscreen = db.Column(
        db.Boolean,
        default=True
    )

    allow_minimize = db.Column(
        db.Boolean,
        default=True
    )

    allow_resize = db.Column(
        db.Boolean,
        default=True
    )

    allow_drag = db.Column(
        db.Boolean,
        default=True
    )

    default_width = db.Column(
        db.Integer,
        default=420
    )

    default_height = db.Column(
        db.Integer,
        default=240
    )

    min_width = db.Column(
        db.Integer,
        default=220
    )

    min_height = db.Column(
        db.Integer,
        default=120
    )

    max_width = db.Column(
        db.Integer,
        default=1200
    )

    max_height = db.Column(
        db.Integer,
        default=900
    )

    floating_mode = db.Column(
        db.Boolean,
        default=True
    )

    start_minimized = db.Column(
        db.Boolean,
        default=False
    )

    always_on_top = db.Column(
        db.Boolean,
        default=True
    )

    # =====================================================
    # TARGET SYSTEM
    # =====================================================

    target_role = db.Column(
        db.String(20),
        default="all"
    )
    # all / user / admin

    target_country = db.Column(
        db.String(100)
    )

    target_language = db.Column(
        db.String(50)
    )

    # =====================================================
    # ANALYTICS
    # =====================================================

    total_views = db.Column(
        db.Integer,
        default=0
    )

    total_clicks = db.Column(
        db.Integer,
        default=0
    )

    total_watch_time = db.Column(
        db.Integer,
        default=0
    )

    total_shares = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # SCHEDULE
    # =====================================================

    start_time = db.Column(
        db.DateTime
    )

    end_time = db.Column(
        db.DateTime
    )

    # =====================================================
    # OWNER
    # =====================================================

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    owner = db.relationship(
        "User",
        backref="live_medias",
        lazy=True
    )

    # =====================================================
    # SECURITY
    # =====================================================

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    is_approved = db.Column(
        db.Boolean,
        default=True
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =====================================================
    # HELPER
    # =====================================================

    def to_dict(self):

        return {

            "id": self.id,

            "title": self.title,

            "description": self.description,

            "media_type": self.media_type,

            "file_url": self.file_url,

            "thumbnail": self.thumbnail,

            "is_live": self.is_live,

            "live_status": self.live_status,

            "force_show": self.force_show,

            "floating_mode": self.floating_mode,

            "allow_fullscreen": self.allow_fullscreen,

            "allow_minimize": self.allow_minimize,

            "allow_resize": self.allow_resize,

            "default_width": self.default_width,

            "default_height": self.default_height,

            "total_views": self.total_views
        }

    # =====================================================
    # DEBUG
    # =====================================================

    def __repr__(self):

        return f"<LiveMedia {self.id} - {self.title}>"
