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
from sqlalchemy import update
import cloudinary.uploader

from extensions import db

from models.live_media import LiveMedia
from models.user import User

live_media_bp = Blueprint(
    "live_media",
    __name__,
    url_prefix="/live"
)

# =========================================================
# ALLOWED FILES
# =========================================================

ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm",
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


def cleanup_old_media(limit=200):

    total = (
        LiveMedia.query
        .filter_by(is_deleted=False)
        .count()
    )

    if total <= limit:
        return

    delete_count = total - limit

    old_medias = (
        LiveMedia.query
        .filter_by(is_deleted=False)
        .order_by(
            LiveMedia.created_at.asc()
        )
        .limit(delete_count)
        .all()
    )

    for media in old_medias:

        try:

            if media.public_id:

                resource_type = (
                    "video"
                    if media.media_type in [
                        "video",
                        "live_tv"
                    ]
                    else "image"
                )

                cloudinary.uploader.destroy(
                    media.public_id,
                    resource_type=resource_type
                )

        except Exception as e:

            print(
                "Cloudinary delete error:",
                e
            )

        db.session.delete(media)

    db.session.commit()
# =========================================================
# LIVE MEDIA PANEL
# =========================================================

@live_media_bp.route("/")
def dashboard():

    if not admin_required():
        flash("Unauthorized", "danger")
        return redirect("/auth/login")

    medias = (
        LiveMedia.query
        .order_by(LiveMedia.id.desc())
        .limit(200)
        .all()
    )

    return render_template(
        "owner/live_media_list.html",
        medias=medias
    )


# =========================================================
# CREATE MEDIA
# =========================================================
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

        filename = secure_filename(file.filename)

        ext = filename.rsplit(".", 1)[1].lower()

        video_extensions = {
            "mp4",
            "mov",
            "avi",
            "mkv",
            "webm"
        }

        try:

            if ext in video_extensions:

                upload_result = cloudinary.uploader.upload_large(
                    file,
                    resource_type="video",
                    folder="live_media",
                    chunk_size=6000000
                )

            else:

                upload_result = cloudinary.uploader.upload(
                    file,
                    resource_type="image",
                    folder="live_media"
                )

        except Exception as e:

            flash(
                f"Upload failed: {e}",
                "danger"
            )

            return redirect(request.url)

        file_url = upload_result["secure_url"]

        public_id = upload_result.get(
            "public_id"
        )

        media = LiveMedia(

            title=title,
            description=description,

            media_type=media_type,
            category=category,

            file_url=file_url,
            public_id=public_id,

            original_filename=filename,

            file_size=upload_result.get(
                "bytes",
                0
            ),

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

        cleanup_old_media(200)

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

@live_media_bp.route(
    "/view/<int:id>",
    methods=["POST"]
)
def update_view(id):

    db.session.execute(

        update(LiveMedia)

        .where(
            LiveMedia.id == id
        )

        .values(
            total_views=
            LiveMedia.total_views + 1
        )

    )

    db.session.commit()

    return jsonify({
        "success": True
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

    try:

        if media.public_id:

            resource_type = (
                "video"
                if media.media_type in [
                    "video",
                    "live_tv"
                ]
                else "image"
            )

            cloudinary.uploader.destroy(
                media.public_id,
                resource_type=resource_type
            )

    except Exception as e:

        print(
            f"Cloudinary delete error: {e}"
        )

    db.session.delete(media)
    db.session.commit()

    flash(
        "Media permanently deleted",
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
