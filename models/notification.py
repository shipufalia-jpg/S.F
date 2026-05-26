from extensions import db
from datetime import datetime


class Notification(db.Model):

    __tablename__ = "notifications"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # USER INFO
    # =====================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    # =====================================================
    # NOTIFICATION CONTENT
    # =====================================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    # =====================================================
    # TYPE
    # =====================================================

    type = db.Column(
        db.String(50),
        default="general",
        index=True
    )

    # examples:
    # general
    # booking
    # payment
    # message
    # warning
    # approve
    # reject
    # block
    # update
    # maintenance

    # =====================================================
    # ICON
    # =====================================================

    icon = db.Column(
        db.String(100),
        default="bell"
    )

    # examples:
    # bell
    # check
    # warning
    # money
    # user
    # message

    # =====================================================
    # IMAGE / BANNER
    # =====================================================

    image = db.Column(
        db.String(500),
        nullable=True
    )

    # notification image/banner

    # =====================================================
    # LINK / REDIRECT
    # =====================================================

    action_url = db.Column(
        db.String(500),
        nullable=True
    )

    # examples:
    # /booking/12
    # /chat/5
    # /wallet

    # =====================================================
    # STATUS
    # =====================================================

    is_read = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    is_sent = db.Column(
        db.Boolean,
        default=False
    )

    # socket/push sent status

    # =====================================================
    # DELIVERY STATUS
    # =====================================================

    delivery_status = db.Column(
        db.String(50),
        default="sent"
    )

    # sent
    # delivered
    # failed
    # seen

    # =====================================================
    # PRIORITY
    # =====================================================

    priority = db.Column(
        db.String(20),
        default="normal"
    )

    # low
    # normal
    # high

    # =====================================================
    # CATEGORY
    # =====================================================

    category = db.Column(
        db.String(100),
        nullable=True
    )

    # marketing
    # security
    # update
    # system

    # =====================================================
    # BROADCAST
    # =====================================================

    is_broadcast = db.Column(
        db.Boolean,
        default=False
    )

    # owner/admin broadcast notification

    # =====================================================
    # PINNED
    # =====================================================

    is_pinned = db.Column(
        db.Boolean,
        default=False
    )

    # important notification

    # =====================================================
    # SOUND
    # =====================================================

    sound = db.Column(
        db.String(100),
        default="default"
    )

    # notification sound

    # =====================================================
    # DEVICE
    # =====================================================

    device = db.Column(
        db.String(50),
        nullable=True
    )

    # android
    # web
    # ios

    # =====================================================
    # SOCKET ROOM
    # =====================================================

    socket_room = db.Column(
        db.String(100),
        nullable=True
    )

    # user_5
    # worker_12

    # =====================================================
    # ANALYTICS
    # =====================================================

    click_count = db.Column(
        db.Integer,
        default=0
    )

    # how many times clicked

    # =====================================================
    # EXPIRE TIME
    # =====================================================

    expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # auto expire notification

    # =====================================================
    # READ TIME
    # =====================================================

    read_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # when user opened notification

    # =====================================================
    # TIMESTAMP
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =====================================================
    # RELATIONSHIP
    # =====================================================

    user = db.relationship(

        "User",

        foreign_keys=[user_id],

        backref=db.backref(

            "notifications",

            lazy=True
        )
    )

    sender = db.relationship(

        "User",

        foreign_keys=[sender_id]
    )

    # =====================================================
    # TO DICT
    # =====================================================

    def to_dict(self):

        return {

            "id": self.id,

            "user_id": self.user_id,

            "sender_id": self.sender_id,

            "title": self.title,

            "message": self.message,

            "type": self.type,

            "icon": self.icon,

            "image": self.image,

            "action_url": self.action_url,

            "is_read": self.is_read,

            "is_deleted": self.is_deleted,

            "is_sent": self.is_sent,

            "delivery_status": self.delivery_status,

            "priority": self.priority,

            "category": self.category,

            "is_broadcast": self.is_broadcast,

            "is_pinned": self.is_pinned,

            "sound": self.sound,

            "device": self.device,

            "socket_room": self.socket_room,

            "click_count": self.click_count,

            "created_at": self.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ) if self.created_at else None,

            "updated_at": self.updated_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ) if self.updated_at else None,

            "read_at": self.read_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ) if self.read_at else None
    }
