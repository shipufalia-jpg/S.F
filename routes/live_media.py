# routes/live_media.py

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session,
    jsonify
)

from werkzeug.utils import secure_filename

from datetime import datetime
import os
import uuid

from extensions import db

from models.live_media import LiveMedia
from models.user import User

live_media_bp = Blueprint(
    "live_media",
    __name__,
    url_prefix="/live"
)

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "..",
    "static",
    "uploads",
    "media_files"
)

ALLOWED_EXTENSIONS = {
    "mp4",
    "mp3",
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif"
}

# =========================================================
# HELPERS
# =========================================================

def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def admin_required():

    return session.get("role") in [
        "admin",
        "super_admin",
        "owner"
    ]


# =========================================================
# LIVE MEDIA PANEL
# =========================================================

@live_media_bp.route("/")
def dashboard():

    if not admin_required():
        flash("Unauthorized", "danger")
        return redirect("/auth/login")

    medias = LiveMedia.query.filter_by(
        is_deleted=False
    ).order_by(
        LiveMedia.id.desc()
    ).all()

    return render_template(
        "owner/live_media_list.html",
        medias=medias
    )


# =========================================================
# CREATE MEDIA
# =========================================================

@live_media_bp.route("/create", methods=["GET", "POST"])
def create_media():

    if not admin_required():
        flash("Unauthorized", "danger")
        return redirect("/auth/login")

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")

        media_type = request.form.get("media_type")
        category = request.form.get("category")

        is_live = bool(request.form.get("is_live"))
        force_show = bool(request.form.get("force_show"))

        floating_mode = bool(request.form.get("floating_mode"))
        auto_play = bool(request.form.get("auto_play"))

        allow_resize = bool(request.form.get("allow_resize"))
        allow_drag = bool(request.form.get("allow_drag"))

        allow_minimize = bool(request.form.get("allow_minimize"))
        allow_fullscreen = bool(request.form.get("allow_fullscreen"))

        default_width = request.form.get(
            "default_width",
            420,
            type=int
        )

        default_height = request.form.get(
            "default_height",
            240,
            type=int
        )

        popup_delay = request.form.get(
            "popup_delay",
            0,
            type=int
        )

        stream_url = request.form.get("stream_url")

        file = request.files.get("file")

        if not file:
            flash("File required", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type", "danger")
            return redirect(request.url)

        # =================================================
        # CREATE FOLDER SAFELY
        # =================================================

        os.makedirs(
            UPLOAD_FOLDER,
            exist_ok=True
        )

        # =================================================
        # SAFE UNIQUE FILENAME
        # =================================================

        filename = secure_filename(file.filename)

        ext = filename.rsplit(".", 1)[1].lower()

        unique_filename = (
            f"{uuid.uuid4().hex}.{ext}"
        )

        save_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        # =================================================
        # SAVE FILE
        # =================================================

        file.save(save_path)

        # =================================================
        # FILE URL
        # =================================================

        file_url = (
            "/static/uploads/media_files/"
            + unique_filename
        )

        # =================================================
        # SAVE DATABASE
        # =================================================

        media = LiveMedia(

            title=title,
            description=description,

            media_type=media_type,
            category=category,

            file_url=file_url,

            original_filename=filename,

            file_size=os.path.getsize(save_path),

            is_live=is_live,

            force_show=force_show,

            floating_mode=floating_mode,

            auto_play=auto_play,

            allow_resize=allow_resize,

            allow_drag=allow_drag,

            allow_minimize=allow_minimize,

            allow_fullscreen=allow_fullscreen,

            default_width=default_width,

            default_height=default_height,

            popup_delay=popup_delay,

            stream_url=stream_url,

            owner_id=session.get("user_id")
        )

        db.session.add(media)
        db.session.commit()

        flash(
            "Live media uploaded successfully",
            "success"
        )

        return redirect("/live")

    return render_template(
        "owner/create.html"
    )


# =========================================================
# UPDATE VIEW
# =========================================================

@live_media_bp.route("/view/<int:id>")
def update_view(id):

    media = LiveMedia.query.get_or_404(id)

    media.total_views += 1

    db.session.commit()

    return jsonify({
        "success": True,
        "views": media.total_views
    })


# =========================================================
# DELETE
# =========================================================

@live_media_bp.route("/delete/<int:id>")
def delete_media(id):

    if not admin_required():
        flash("Unauthorized", "danger")
        return redirect("/auth/login")

    media = LiveMedia.query.get_or_404(id)

    media.is_deleted = True

    db.session.commit()

    flash(
        "Media deleted",
        "success"
    )

    return redirect("/live")


# =========================================================
# TOGGLE ACTIVE
# =========================================================

@live_media_bp.route("/toggle/<int:id>")
def toggle_media(id):

    if not admin_required():
        flash("Unauthorized", "danger")
        return redirect("/auth/login")

    media = LiveMedia.query.get_or_404(id)

    media.is_active = not media.is_active

    db.session.commit()

    flash(
        "Media status updated",
        "success"
    )

    return redirect("/live")


# =========================================================
# FORCE SHOW
# =========================================================

@live_media_bp.route("/force/<int:id>")
def force_media(id):

    if not admin_required():
        flash("Unauthorized", "danger")
        return redirect("/auth/login")

    media = LiveMedia.query.get_or_404(id)

    media.force_show = not media.force_show

    db.session.commit()

    flash(
        "Force show updated",
        "success"
    )

    return redirect("/live")


# =========================================================
# LIVE STATUS
# =========================================================

@live_media_bp.route("/status/<int:id>", methods=["POST"])
def update_live_status(id):

    if not admin_required():
        return jsonify({
            "success": False
        }), 403

    media = LiveMedia.query.get_or_404(id)

    status = request.form.get("status")

    allowed = [
        "offline",
        "live",
        "scheduled"
    ]

    if status not in allowed:
        return jsonify({
            "success": False,
            "message": "Invalid status"
        })

    media.live_status = status

    db.session.commit()

    return jsonify({
        "success": True,
        "status": status
    })


# =========================================================
# FULLSCREEN API
# =========================================================

@live_media_bp.route("/fullscreen/<int:id>")
def fullscreen_player(id):

    media = LiveMedia.query.get_or_404(id)

    return render_template(
        "live_media/fullscreen.html",
        media=media
        )
