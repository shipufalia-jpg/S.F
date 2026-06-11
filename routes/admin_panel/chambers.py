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
from models.doctor import Doctor
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

@admin_chambers.route("/chamber/<int:chamber_id>")
def chamber_details(chamber_id):

    admin_id = session.get("user_id")

    chamber = Chamber.query.filter_by(
        id=chamber_id,
        created_by_admin_id=admin_id
    ).first_or_404()

    profile = ChamberProfile.query.filter_by(
        chamber_id=chamber.id
    ).first()

    doctors = Doctor.query.filter_by(
        chamber_id=chamber.id
    ).all()

    return render_template(
        "admin/chamber_details.html",
        chamber=chamber,
        profile=profile,
        doctors=doctors
    )

# ==========================================
# CREATE CHAMBER
# ==========================================

@admin_chambers.route("/chamber/create", methods=["GET", "POST"])
def create_chamber():

    if request.method == "POST":

        admin_id = session.get("user_id")

        if not admin_id:
            flash("Login required", "danger")
            return redirect("/login")

        admin = User.query.get(admin_id)

        username = request.form.get("username")
        password = request.form.get("password")

        if Chamber.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("admin_chambers.create_chamber"))

        # ======================
        # CREATE CHAMBER
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
        def upload(file, folder):
            if file and file.filename:
                result = cloudinary.uploader.upload(file, folder=folder)
                return result["secure_url"]
            return None

        profile_image_path = upload(request.files.get("profile_image"), "chambers/profile")
        cover_image_path = upload(request.files.get("cover_image"), "chambers/cover")
        logo_path = upload(request.files.get("logo"), "chambers/logo")

        # ======================
        # PROFILE CREATE
        # ======================
        profile = ChamberProfile(
            chamber_id=chamber.id,
            chamber_name=request.form.get("name"),
            phone=request.form.get("phone"),
            whatsapp=request.form.get("whatsapp"),
            email=request.form.get("email"),
            website=request.form.get("website"),
            area=request.form.get("area"),
            address=request.form.get("address"),
            description=request.form.get("description"),
            profile_image=profile_image_path,
            cover_image=cover_image_path,
            logo=logo_path
        )

        db.session.add(profile)
        db.session.commit()

        flash("Chamber & Profile created successfully.", "success")

        return redirect(url_for("admin_chambers.chambers"))

    return render_template("admin/create_chamber.html")
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

    profile = ChamberProfile.query.filter_by(
        chamber_id=chamber.id
    ).first()

    if request.method == "POST":

        # ======================
        # CHAMBER BASIC INFO
        # ======================
        chamber.name = request.form.get("name")
        chamber.phone = request.form.get("phone")
        chamber.address = request.form.get("address")

        # ======================
        # PROFILE UPDATE
        # ======================
        if profile:

            profile.chamber_name = request.form.get("name")
            profile.phone = request.form.get("phone")
            profile.whatsapp = request.form.get("whatsapp")
            profile.email = request.form.get("email")
            profile.website = request.form.get("website")
            profile.area = request.form.get("area")
            profile.address = request.form.get("address")
            profile.description = request.form.get("description")

            # ======================
            # IMAGE UPDATE (Cloudinary)
            # ======================
            def upload(file, folder):
                if file and file.filename:
                    result = cloudinary.uploader.upload(file, folder=folder)
                    return result["secure_url"]
                return None

            new_profile_img = upload(request.files.get("profile_image"), "chambers/profile")
            new_cover_img = upload(request.files.get("cover_image"), "chambers/cover")
            new_logo = upload(request.files.get("logo"), "chambers/logo")

            if new_profile_img:
                profile.profile_image = new_profile_img

            if new_cover_img:
                profile.cover_image = new_cover_img

            if new_logo:
                profile.logo = new_logo

        db.session.commit()

        flash("Chamber updated successfully.", "success")

        return redirect(
            url_for("admin_chambers.chamber_details", chamber_id=chamber.id)
        )

    return render_template(
        "admin/edit_chamber.html",
        chamber=chamber,
        profile=profile
            )

@admin_chambers.route("/doctor/<int:doctor_id>")
def doctor_details(doctor_id):

    # ======================
    # SESSION CHECK
    # ======================
    admin_id = session.get("user_id")
    chamber_session = session.get("chamber_id")

    if not admin_id and not chamber_session:
        return redirect("/login")

    # ======================
    # GET DOCTOR
    # ======================
    doctor = Doctor.query.get_or_404(doctor_id)

    # ======================
    # CHAMBER SECURITY CHECK
    # (doctor অন্য chamber এর হলে access block)
    # ======================
    if chamber_session and doctor.chamber_id != chamber_session:
        flash("Access Denied", "danger")
        return redirect("/chamber/dashboard")

    # ======================
    # OPTIONAL: LOAD CHAMBER INFO
    # ======================
    chamber = None
    if doctor.chamber_id:
        chamber = Chamber.query.get(doctor.chamber_id)

    # ======================
    # RENDER
    # ======================
    return render_template(
        "doctor/view_doctor.html",
        doctor=doctor,
        chamber=chamber
    )

@admin_chambers.route(
    "/doctor/<int:doctor_id>/edit",
    methods=["GET", "POST"]
)
def edit_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == "POST":

        doctor.name = request.form.get("name")
        doctor.degree = request.form.get("degree")
        doctor.specialization = request.form.get("specialization")
        doctor.hospital = request.form.get("hospital")
        doctor.experience = request.form.get("experience")
        doctor.about = request.form.get("about")

        def upload(file, folder):
            if file and file.filename:
                result = cloudinary.uploader.upload(file, folder=folder)
                return result["secure_url"]
            return None

        new_profile = upload(request.files.get("profile_photo"), "doctors/profile")
        new_cover = upload(request.files.get("cover_photo"), "doctors/cover")

        if new_profile:
            doctor.profile_photo = new_profile

        if new_cover:
            doctor.cover_photo = new_cover

        db.session.commit()

        flash("Doctor updated successfully", "success")

        return redirect(url_for("admin_chambers.doctor_details", doctor_id=doctor.id))

    return render_template("doctor/edit_doctor.html", doctor=doctor)


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

    admin_id = session.get("user_id")
    chamber_session = session.get("chamber_id")

    if not admin_id and not chamber_session:
        return redirect("/login")

    if chamber_session and chamber_session != chamber_id:
        flash("Access Denied", "danger")
        return redirect("/chamber/dashboard")

    chamber = Chamber.query.get_or_404(chamber_id)

    if request.method == "POST":

        # ======================
        # CLOUDINARY UPLOAD
        # ======================
        def upload(file, folder):
            if file and file.filename:
                result = cloudinary.uploader.upload(file, folder=folder)
                return result["secure_url"]
            return None

        profile_photo_url = upload(
            request.files.get("profile_photo"),
            "doctors/profile"
        )

        cover_photo_url = upload(
            request.files.get("cover_photo"),
            "doctors/cover"
        )

        # ======================
        # CREATE DOCTOR
        # ======================
        doctor = Doctor(
            chamber_id=chamber.id,
            name=request.form.get("name"),
            degree=request.form.get("degree"),
            specialization=request.form.get("specialization"),
            hospital=request.form.get("hospital"),
            experience=request.form.get("experience"),
            about=request.form.get("about"),
            profile_photo=profile_photo_url,
            cover_photo=cover_photo_url
        )

        db.session.add(doctor)
        db.session.commit()

        flash("Doctor Added Successfully", "success")

        if admin_id:
            return redirect("/admin/chambers")

        return redirect("/chamber/dashboard")

    return render_template(
        "doctor/create_doctor.html",
        chamber=chamber
    )
