from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from extensions import db

from models.user import User
from models.chamber import Chamber
import cloudinary
import cloudinary.uploader
from models.chamber_profile import ChamberProfile


admin_chambers = Blueprint(
    "admin_chambers",
    __name__,
    url_prefix="/admin"
)


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@admin_chambers.route("/dashboard")
def dashboard():

    admin_id = session.get("user_id")

    chambers = Chamber.query.filter_by(
        created_by_admin_id=admin_id
    ).all()

    return render_template(
        "admin/dashboard.html",
        chambers=chambers,
        total_chambers=len(chambers)
    )


# ==========================================
# MY CHAMBERS
# ==========================================

@admin_chambers.route("/chambers")
def chambers():

    admin_id = session.get("user_id")

    chambers = Chamber.query.filter_by(
        created_by_admin_id=admin_id
    ).order_by(
        Chamber.id.desc()
    ).all()

    return render_template(
        "admin/chambers.html",
        chambers=chambers
    )


# ==========================================
# CHAMBER DETAILS
# ==========================================

@admin_chambers.route(
    "/chamber/<int:chamber_id>"
)
def chamber_details(chamber_id):

    admin_id = session.get("user_id")

    chamber = Chamber.query.filter_by(
        id=chamber_id,
        created_by_admin_id=admin_id
    ).first_or_404()

    return render_template(
        "admin/chamber_details.html",
        chamber=chamber
    )


# ==========================================
# CREATE CHAMBER
# ==========================================

@admin_chambers.route(
    "/chamber/create",
    methods=["GET", "POST"]
)
def create_chamber():

    if request.method == "POST":

        admin_id = session.get("user_id")

        if not admin_id:
            flash("Login required", "danger")
            return redirect("/login")

        admin = User.query.get(admin_id)

        username = request.form.get("username")
        password = request.form.get("password")

        exists = Chamber.query.filter_by(
            username=username
        ).first()

        if exists:
            flash(
                "Username already exists.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_chambers.create_chamber"
                )
            )

        # ======================
        # CREATE CHAMBER ACCOUNT
        # ======================

        chamber = Chamber(
            name=request.form.get("name"),
            username=username,
            phone=request.form.get("phone"),
            created_by_admin_id=admin_id,
            controller_admin_id=admin_id,
            super_admin_id=admin.controller_id,
            owner_id=None
        )

        chamber.set_password(password)

        db.session.add(chamber)
        db.session.flush()

        # ======================
        # CLOUDINARY UPLOAD
        # ======================

        profile_image_path = None
        cover_image_path = None
        logo_path = None

        profile_image = request.files.get(
            "profile_image"
        )

        if profile_image and profile_image.filename:

            result = cloudinary.uploader.upload(
                profile_image,
                folder="chambers/profile"
            )

            profile_image_path = result[
                "secure_url"
            ]

        cover_image = request.files.get(
            "cover_image"
        )

        if cover_image and cover_image.filename:

            result = cloudinary.uploader.upload(
                cover_image,
                folder="chambers/cover"
            )

            cover_image_path = result[
                "secure_url"
            ]

        logo = request.files.get(
            "logo"
        )

        if logo and logo.filename:

            result = cloudinary.uploader.upload(
                logo,
                folder="chambers/logo"
            )

            logo_path = result[
                "secure_url"
            ]

        # ======================
        # CREATE PROFILE
        # ======================

        profile = ChamberProfile(

            chamber_id=chamber.id,

            chamber_name=request.form.get(
                "name"
            ),

            phone=request.form.get(
                "phone"
            ),

            whatsapp=request.form.get(
                "whatsapp"
            ),

            email=request.form.get(
                "email"
            ),

            website=request.form.get(
                "website"
            ),

            area=request.form.get(
                "area"
            ),

            address=request.form.get(
                "address"
            ),

            description=request.form.get(
                "description"
            ),

            profile_image=profile_image_path,
            cover_image=cover_image_path,
            logo=logo_path
        )

        db.session.add(profile)
        db.session.commit()

        flash(
            "Chamber & Profile created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin_chambers.chambers"
            )
        )

    return render_template(
        "admin/create_chamber.html"
    )
# ==========================================
# EDIT CHAMBER
# ==========================================

@admin_chambers.route(
    "/chamber/<int:chamber_id>/edit",
    methods=["GET", "POST"]
)
def edit_chamber(chamber_id):

    admin_id = session.get("user_id")

    chamber = Chamber.query.filter_by(
        id=chamber_id,
        created_by_admin_id=admin_id
    ).first_or_404()

    if request.method == "POST":

        chamber.name = request.form.get(
            "name"
        )

        chamber.phone = request.form.get(
            "phone"
        )

        chamber.address = request.form.get(
            "address"
        )

        db.session.commit()

        flash(
            "Chamber updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin_chambers.chamber_details",
                chamber_id=chamber.id
            )
        )

    return render_template(
        "admin/edit_chamber.html",
        chamber=chamber
    )


# ==========================================
# RESET CHAMBER PASSWORD
# ==========================================

@admin_chambers.route(
    "/chamber/<int:chamber_id>/reset-password",
    methods=["GET", "POST"]
)
def reset_password(chamber_id):

    admin_id = session.get("user_id")

    chamber = Chamber.query.filter_by(
        id=chamber_id,
        created_by_admin_id=admin_id
    ).first_or_404()

    if request.method == "POST":

        new_password = request.form.get(
            "password"
        )

        if not new_password:

            flash(
                "Password required.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin_chambers.reset_password",
                    chamber_id=chamber.id
                )
            )

        chamber.set_password(
            new_password
        )

        db.session.commit()

        flash(
            "Password reset successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin_chambers.chamber_details",
                chamber_id=chamber.id
            )
        )

    return render_template(
        "admin/reset_password.html",
        chamber=chamber
  )


@admin_chambers.route(
    "/doctor/create/<int:chamber_id>",
    methods=["GET", "POST"]
)
def create_doctor(chamber_id):

    # Admin Login
    admin_id = session.get("user_id")

    # Chamber Login
    chamber_session = session.get("chamber_id")

    # Login Check
    if not admin_id and not chamber_session:
        return redirect("/login")

    # Chamber Owner শুধু নিজের Chamber-এ Add করতে পারবে
    if chamber_session and chamber_session != chamber_id:
        flash(
            "Access Denied",
            "danger"
        )
        return redirect("/chamber/dashboard")

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    if request.method == "POST":

        doctor = Doctor(
            chamber_id=chamber.id,
            name=request.form.get("name"),
            degree=request.form.get("degree"),
            specialization=request.form.get("specialization"),
            hospital=request.form.get("hospital"),
            experience=request.form.get("experience"),
            about=request.form.get("about")
        )

        db.session.add(doctor)
        db.session.commit()

        flash(
            "Doctor Added Successfully",
            "success"
        )

        # Admin হলে
        if admin_id:
            return redirect(
                "/admin/chambers"
            )

        # Chamber Owner হলে
        return redirect(
            "/chamber/dashboard"
        )

    return render_template(
        "doctor/create_doctor.html",
        chamber=chamber
    )
