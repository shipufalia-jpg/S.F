from flask import session
from models.chat import Chat
from extensions import db
from datetime import datetime
from decorators.auth import owner_only
from flask import Blueprint

owner_chat = Blueprint('owner_chat', __name__)


@owner_chat.route('/owner/chats')
@owner_only
def all_chats():

    chats = Chat.query.filter_by(
        is_deleted=False,
        is_blocked=False
    ).order_by(Chat.id.desc()).all()

    return render_template("owner_chat_monitor.html", chats=chats)
    
# ================= OWNER CHAT BLOCK =================
@owner_chat.route('/owner/chat/block/<int:id>')
@owner_only
def block_chat(id):

    chat = Chat.query.get(id)

    if not chat:
        return "Chat not found"

    # 🔒 already blocked check
    if chat.is_blocked:
        return "Already blocked"

    chat.is_blocked = True
    chat.blocked_by = session.get('user_id')
    chat.blocked_at = datetime.utcnow()

    db.session.commit()

    return "Chat blocked 🚫"


# ================= OWNER CHAT DELETE =================
@owner_chat.route('/owner/chat/delete/<int:id>')
@owner_only
def delete_chat(id):

    chat = Chat.query.get(id)

    if not chat:
        return "Chat not found"

    # 🗑 soft delete (SAAS SAFE)
    chat.is_deleted = True
    chat.deleted_by = session.get('user_id')
    chat.deleted_at = datetime.utcnow()

    db.session.commit()

    return "Chat deleted 🗑"
    
# ================= OWNER CHAT UNBLOCK =================
@owner_chat.route('/owner/chat/unblock/<int:id>')
@owner_only
def unblock_chat(id):

    chat = Chat.query.get(id)

    if not chat:
        return "Chat not found"

    # 🔒 already active check
    if not chat.is_blocked:
        return "Chat already active"

    chat.is_blocked = False
    chat.blocked_by = None
    chat.blocked_at = None

    db.session.commit()

    return "Chat unblocked ✅"