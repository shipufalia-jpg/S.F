# services/confirm_service.py

from flask import request

def confirm(action):
    if request.args.get("confirm") != "yes":
        return f"""
        <h3>⚠ Are you sure to {action}?</h3>
        <a href='?confirm=yes'>✔ Yes</a> |
        <a href='javascript:history.back()'>❌ No</a>
        """
    return None