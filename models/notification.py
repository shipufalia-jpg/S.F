from extensions import db
from datetime import datetime

class Notification(db.Model):

__tablename__ = "notifications"  

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

# =========================  
# USER INFO  
# =========================  

user_id = db.Column(  
    db.Integer,  
    db.ForeignKey('user.id'),  
    nullable=False  
)  

sender_id = db.Column(  
    db.Integer,  
    db.ForeignKey('user.id'),  
    nullable=True  
)  

# =========================  
# NOTIFICATION CONTENT  
# =========================  

title = db.Column(  
    db.String(255),  
    nullable=False  
)  

message = db.Column(  
    db.Text,  
    nullable=False  
)  

# =========================  
# TYPE  
# =========================  

type = db.Column(  
    db.String(50),  
    default="general"  
)  

# example:  
# general  
# booking  
# payment  
# message  
# warning  
# approve  
# reject  
# block  

# =========================  
# ICON  
# =========================  

icon = db.Column(  
    db.String(100),  
    default="bell"  
)  

# example:  
# bell  
# check  
# warning  
# money  
# user  
# message  

# =========================  
# LINK / REDIRECT  
# =========================  

action_url = db.Column(  
    db.String(500),  
    nullable=True  
)  

# example:  
# /booking/12  
# /chat/5  
# /wallet  

# =========================  
# STATUS  
# =========================  

is_read = db.Column(  
    db.Boolean,  
    default=False  
)  

is_deleted = db.Column(  
    db.Boolean,  
    default=False  
)  

# =========================  
# PRIORITY  
# =========================  

priority = db.Column(  
    db.String(20),  
    default="normal"  
)  

# low  
# normal  
# high  

# =========================  
# REALTIME  
# =========================  

is_sent = db.Column(  
    db.Boolean,  
    default=False  
)  

# socket/push sent status  

# =========================  
# DEVICE  
# =========================  

device = db.Column(  
    db.String(50),  
    nullable=True  
)  

# android  
# web  
# ios  

# =========================  
# TIMESTAMP  
# =========================  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)  

updated_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow,  
    onupdate=datetime.utcnow  
)  

# =========================  
# RELATIONSHIP  
# =========================  

user = db.relationship(  
    "User",  
    foreign_keys=[user_id],  
    backref="notifications"  
)  

sender = db.relationship(  
    "User",  
    foreign_keys=[sender_id]  
)  

# =========================  
# TO DICT  
# =========================  

def to_dict(self):  

    return {  

        "id": self.id,  
        "title": self.title,  
        "message": self.message,  
        "type": self.type,  
        "icon": self.icon,  
        "action_url": self.action_url,  
        "is_read": self.is_read,  
        "priority": self.priority,  
        "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")  
    }


