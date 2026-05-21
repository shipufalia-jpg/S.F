from models.activity_log import ActivityLog
from extensions import db
from flask import request

def log_activity(actor_id, target_id, action, role, meta=None):
    log = ActivityLog(
        actor_id=actor_id,
        target_id=target_id,
        action=action,
        role=role,
        meta=meta,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
  