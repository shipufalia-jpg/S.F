from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from models.profile import Profile
from models import Profile, Work
from models.user import User
from models.work_model import Work

from extensions import db

from PIL import Image

import cloudinary
import cloudinary.uploader

import os
import json
import uuid
import tempfile


# ================= CLOUDINARY =================

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


profile_bp = Blueprint(
    "profile",
    __name__
)


# ================= IMAGE SETTINGS =================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ================= IMAGE RESIZE =================

def resize_image(
    input_path,
    output_path,
    size
):

    with Image.open(
        input_path
    ) as img:

        img = img.convert(
            "RGB"
        )

        img.thumbnail(
            size,
            Image.LANCZOS
        )

        img.save(
            output_path,
            format="JPEG",
            quality=85,
            optimize=True
        )


# ================= CLOUDINARY UPLOAD =================

def save_image_cloudinary(
    file,
    folder,
    size=(800, 800)
):

    # ================= FILE CHECK =================

    if not file:
        raise ValueError(
            "No file provided"
        )

    if "." not in file.filename:
        raise ValueError(
            "Invalid filename"
        )

    ext = file.filename.rsplit(
        ".",
        1
    )[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Only JPG, JPEG, PNG, WEBP allowed"
        )

    # ================= SIZE CHECK =================

    file.seek(
        0,
        os.SEEK_END
    )

    file_size = file.tell()

    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            "Image size must be under 5MB"
        )

    temp_input = None
    temp_output = None

    try:

        # ================= TEMP INPUT =================

        temp_input = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{ext}"
        )

        file.save(
            temp_input.name
        )

        # ================= TEMP OUTPUT =================

        temp_output = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        resize_image(
            temp_input.name,
            temp_output.name,
            size
        )

        # ================= CLOUDINARY =================

        result = cloudinary.uploader.upload(
            temp_output.name,
            folder=folder,
            public_id=uuid.uuid4().hex,
            overwrite=False,
            resource_type="image"
        )

        return result["secure_url"]

    except Exception as e:

        raise Exception(
            f"Upload Failed: {str(e)}"
        )

    finally:

        # ================= CLEANUP =================

        if (
            temp_input and
            os.path.exists(
                temp_input.name
            )
        ):
            try:
                os.remove(
                    temp_input.name
                )
            except Exception:
                pass

        if (
            temp_output and
            os.path.exists(
                temp_output.name
            )
        ):
            try:
                os.remove(
                    temp_output.name
                )
            except Exception:
                pass

# ================= MY PROFILE =================

@profile_bp.route('/profile')
def my_profile():

    if 'user_id' not in session:
        return redirect('/auth/login')

    user = db.session.get(
        User,
        session['user_id']
    )

    if not user:
        return redirect('/auth/login')

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    gallery = []

    if profile and profile.gallery:

        try:

            gallery = json.loads(
                profile.gallery
            )

        except:

            gallery = []

    return render_template(
        "profile.html",
        user=user,
        profile=profile,
        gallery=gallery
    )


# ================= VIEW OTHER PROFILE =================

@profile_bp.route('/profile/<int:user_id>')
def view_profile(user_id):

    # ================= USER =================

    viewed_user = User.query.get_or_404(
        user_id
    )

    # ================= PROFILE =================

    profile = Profile.query.filter_by(
        user_id=user_id
    ).first()

    # ================= WORK =================

    works = Work.query.filter_by(
        user_id=user_id
    ).order_by(
        Work.id.desc()
    ).all()

    # ================= GALLERY =================

    gallery = []

    if profile and profile.gallery:

        try:

            gallery = json.loads(
                profile.gallery
            )

            if not isinstance(gallery, list):

                gallery = []

        except Exception:

            gallery = []

    # ================= RENDER =================

    return render_template(

        "profile.html",

        user=viewed_user,

        profile=profile,

        works=works,

        gallery=gallery
    )

        

# ================= PROFILE SETUP =================

@profile_bp.route(
    '/profile/setup',
    methods=['GET', 'POST']
)
def profile_setup():

    if 'user_id' not in session:
        return redirect('/auth/login')

    user = db.session.get(
        User,
        session['user_id']
    )

    if not user:
        return redirect('/auth/login')

    # ================= FIND PROFILE =================

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    # ================= CREATE PROFILE =================

    if not profile:

        profile = Profile(
            user_id=user.id
        )

        db.session.add(profile)

        db.session.commit()

    # ================= GET REQUEST =================

    if request.method == 'GET':

        gallery = []

        if profile.gallery:

            try:

                gallery = json.loads(
                    profile.gallery
                )

            except:

                gallery = []

        return render_template(
            "edit_profile.html",
            user=user,
            profile=profile,
            gallery=gallery
        )

    # ================= POST REQUEST =================

    try:

        profile.name = request.form.get(
            'name',
            ''
        )

        profile.address = request.form.get(
            'address',
            ''
        )

        age = request.form.get(
            'age'
        )

        if age and age.isdigit():

            profile.age = int(age)

        profile.education = request.form.get(
            'education',
            ''
        )

        profile.area = request.form.get(
            'area',
            ''
        )

        profile.gender = request.form.get(
            'gender',
            ''
        )

        profile.religion = request.form.get(
            'religion',
            ''
        )

        profile.country = request.form.get(
            'country',
            ''
        )

        profile.work_desc = request.form.get(
            'work_desc',
            ''
        )

    except Exception as e:

        return f"Form Error: {e}"

    # ================= PROFILE IMAGE =================

    profile_img = request.files.get(
        'profile_img'
    )

    if (
        profile_img and
        profile_img.filename != ''
    ):

        profile.profile_img = save_image_cloudinary(
            profile_img,
            folder="sf_works_hub/profile",
            size=(600, 600)
        )

    # ================= COVER IMAGE =================

    cover_img = request.files.get(
        'cover_img'
    )

    if (
        cover_img and
        cover_img.filename != ''
    ):

        profile.cover_img = save_image_cloudinary(
            cover_img,
            folder="sf_works_hub/cover",
            size=(1400, 600)
        )

    # ================= GALLERY =================

    gallery_files = request.files.getlist(
        'gallery'
    )

    gallery_list = []

    if profile.gallery:

        try:

            gallery_list = json.loads(
                profile.gallery
            )

        except:

            gallery_list = []

    for file in gallery_files:

        if (
            file and
            file.filename != ''
        ):

            img_url = save_image_cloudinary(
                file,
                folder="sf_works_hub/gallery",
                size=(1200, 1200)
            )

            gallery_list.append(
                img_url
            )

    profile.gallery = json.dumps(
        gallery_list
    )

    # ================= SAVE DATABASE =================

    try:

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        return (
            f"Database Error: {e}"
        )

    return redirect('/profile')


# ================= DELETE GALLERY IMAGE =================

@profile_bp.route(
    '/delete-gallery-image/<int:index>'
)
def delete_gallery_image(index):

    if 'user_id' not in session:
        return redirect('/auth/login')

    profile = Profile.query.filter_by(
        user_id=session['user_id']
    ).first()

    if not profile:
        return redirect('/profile')

    gallery = []

    if profile.gallery:

        try:

            gallery = json.loads(
                profile.gallery
            )

        except:

            gallery = []

    if 0 <= index < len(gallery):

        gallery.pop(index)

        profile.gallery = json.dumps(
            gallery
        )

        db.session.commit()

    return redirect('/profile')
    
