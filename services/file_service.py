import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(file):
    if not file or file.filename == "":
        return None

    # 🔴 file type check
    if not allowed_file(file.filename):
        return "Invalid file type"

    # 🔐 secure name + unique id
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # 📁 dynamic path from config
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)

    file.save(path)

    return f"static/uploads/{filename}"