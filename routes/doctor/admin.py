from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from extensions import db
from models.doctor import Doctor
from models.doctor.chamber import Chamber

from . import doctor_bp
print("ADMIN LOADED")


# ==========================================
# CREATE DOCTOR
# ==========================================

@doctor_bp.route(
    "/admin/create",
    methods=["GET", "POST"]
)
def create_doctor():

    if request.method == "POST":

        doctor = Doctor(
            name=request.form.get("name"),
            degree=request.form.get("degree"),
            specialization=request.form.get("specialization"),
            hospital=request.form.get("hospital"),
            experience=request.form.get("experience"),
            about=request.form.get("about"),
            profile_photo=request.form.get("profile_photo"),
            cover_photo=request.form.get("cover_photo"),
            verified=bool(request.form.get("verified"))
        )

        db.session.add(doctor)
        db.session.commit()

        flash(
            "Doctor created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "doctor.manage_chambers",
                doctor_id=doctor.id
            )
        )

    return render_template(
        "doctor/create.html"
    )


# ==========================================
# EDIT DOCTOR
# ==========================================

@doctor_bp.route(
    "/admin/<int:doctor_id>/edit",
    methods=["GET", "POST"]
)
def edit_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    if request.method == "POST":

        doctor.name = request.form.get("name")
        doctor.degree = request.form.get("degree")
        doctor.specialization = request.form.get("specialization")
        doctor.hospital = request.form.get("hospital")
        doctor.experience = request.form.get("experience")
        doctor.about = request.form.get("about")
        doctor.profile_photo = request.form.get("profile_photo")
        doctor.cover_photo = request.form.get("cover_photo")
        doctor.verified = bool(
            request.form.get("verified")
        )

        db.session.commit()

        flash(
            "Doctor updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "doctor.doctor_profile",
                doctor_id=doctor.id
            )
        )

    return render_template(
        "doctor/edit.html",
        doctor=doctor
    )


# ==========================================
# DELETE DOCTOR
# ==========================================

@doctor_bp.route(
    "/admin/<int:doctor_id>/delete"
)
def delete_doctor(doctor_id):

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    db.session.delete(doctor)
    db.session.commit()

    flash(
        "Doctor deleted successfully.",
        "success"
    )

    return redirect(
        url_for("doctor.doctor_list")
    )


# ==========================================
# CHAMBER MANAGER
# ==========================================

@doctor_bp.route(
    "/admin/<int:doctor_id>/chambers"
)
def manage_chambers(doctor_id):

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    return render_template(
        "doctor/chambers.html",
        doctor=doctor
    )


# ==========================================
# ADD CHAMBER
# ==========================================

@doctor_bp.route(
    "/admin/<int:doctor_id>/chamber/add",
    methods=["GET", "POST"]
)
def add_chamber(doctor_id):

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    if request.method == "POST":

        chamber = Chamber(
            doctor_id=doctor.id,
            chamber_name=request.form.get(
                "chamber_name"
            ),
            area=request.form.get("area"),
            address=request.form.get("address"),
            phone=request.form.get("phone"),
            whatsapp=request.form.get(
                "whatsapp"
            ),
            day=request.form.get("day"),
            start_time=request.form.get(
                "start_time"
            ),
            end_time=request.form.get(
                "end_time"
            )
        )

        db.session.add(chamber)
        db.session.commit()

        flash(
            "Chamber added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "doctor.manage_chambers",
                doctor_id=doctor.id
            )
        )

    return render_template(
        "doctor/add_chamber.html",
        doctor=doctor
    )


# ==========================================
# EDIT CHAMBER
# ==========================================

@doctor_bp.route(
    "/admin/chamber/<int:chamber_id>/edit",
    methods=["GET", "POST"]
)
def edit_chamber(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    if request.method == "POST":

        chamber.chamber_name = request.form.get(
            "chamber_name"
        )
        chamber.area = request.form.get("area")
        chamber.address = request.form.get(
            "address"
        )
        chamber.phone = request.form.get(
            "phone"
        )
        chamber.whatsapp = request.form.get(
            "whatsapp"
        )
        chamber.day = request.form.get("day")
        chamber.start_time = request.form.get(
            "start_time"
        )
        chamber.end_time = request.form.get(
            "end_time"
        )

        db.session.commit()

        flash(
            "Chamber updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "doctor.manage_chambers",
                doctor_id=chamber.doctor_id
            )
        )

    return render_template(
        "doctor/edit_chamber.html",
        chamber=chamber
    )


# ==========================================
# DELETE CHAMBER
# ==========================================

@doctor_bp.route(
    "/admin/chamber/<int:chamber_id>/delete"
)
def delete_chamber(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    doctor_id = chamber.doctor_id

    db.session.delete(chamber)
    db.session.commit()

    flash(
        "Chamber deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "doctor.manage_chambers",
            doctor_id=doctor_id
        )
    )


# ==========================================
# ADMIN DOCTORS PANEL
# ==========================================

@doctor_bp.route("/admin")
def admin_doctors():

    q = request.args.get("q", "").strip()

    doctors = Doctor.query

    if q:
        doctors = doctors.filter(
            db.or_(
                Doctor.name.ilike(f"%{q}%"),
                Doctor.specialization.ilike(f"%{q}%"),
                Doctor.hospital.ilike(f"%{q}%")
            )
        )

    doctors = doctors.order_by(
        Doctor.id.desc()
    ).all()

    total_doctors = Doctor.query.count()

    total_chambers = Chamber.query.count()

    verified_doctors = Doctor.query.filter_by(
        verified=True
    ).count()

    return render_template(
        "doctor/admin_doctors.html",
        doctors=doctors,
        total_doctors=total_doctors,
        total_chambers=total_chambers,
        verified_doctors=verified_doctors
        )
