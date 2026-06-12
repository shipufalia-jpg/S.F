from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash
)

from extensions import db

from models.chamber import Chamber
from models.doctor.doctor import Doctor
from models.appointment import Appointment
from models.chamber import ChamberRating
from models.chamber_profile import ChamberProfile


chamber_panel = Blueprint(
    "chamber_panel",
    __name__,
    url_prefix="/chamber"
)


# ==========================================
# DASHBOARD
# ==========================================

@chamber_panel.route("/dashboard")
def dashboard():

    chamber_id = session.get("chamber_id")

    if not chamber_id:
        return redirect("/chamber/login")

    total_doctors = Doctor.query.filter_by(
        chamber_id=chamber_id
    ).count()

    total_bookings = Appointment.query.filter_by(
        chamber_id=chamber_id
    ).count()

    recent_bookings = Appointment.query.filter_by(
        chamber_id=chamber_id
    ).order_by(
        Appointment.id.desc()
    ).limit(10).all()

    return render_template(
        "chamber/dashboard.html",
        total_doctors=total_doctors,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )


# ==========================================
# CHAMBER PROFILE
# ==========================================
@chamber_panel.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    chamber_id = session.get("chamber_id")

    if not chamber_id:
        return redirect("/chamber/login")

    profile = ChamberProfile.query.filter_by(
        chamber_id=chamber_id
    ).first()
    
    if not profile:

        profile = ChamberProfile(
            chamber_id=chamber_id,
            chamber_name=session.get(
                "chamber_name",
                "My Chamber"
            )
        )

        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":

        # ======================
        # BASIC INFO
        # ======================

        profile.chamber_name = request.form.get(
            "chamber_name"
        )

        profile.phone = request.form.get(
            "phone"
        )

        profile.whatsapp = request.form.get(
            "whatsapp"
        )

        profile.email = request.form.get(
            "email"
        )

        profile.website = request.form.get(
            "website"
        )

        profile.area = request.form.get(
            "area"
        )

        profile.address = request.form.get(
            "address"
        )

        profile.description = request.form.get(
            "description"
        )

        # ======================
        # PROFILE IMAGE
        # ======================

        profile_file = request.files.get(
            "profile_image"
        )

        if profile_file and profile_file.filename:

            result = upload(
                profile_file,
                folder="chambers/profile"
            )

            profile.profile_image = result[
                "secure_url"
            ]

        # ======================
        # COVER IMAGE
        # ======================

        cover_file = request.files.get(
            "cover_image"
        )

        if cover_file and cover_file.filename:

            result = upload(
                cover_file,
                folder="chambers/cover"
            )

            profile.cover_image = result[
                "secure_url"
            ]

        db.session.commit()

        flash(
            "Profile updated successfully",
            "success"
        )

        return redirect(
            "/chamber/profile"
        )

    return render_template(
        "chamber/profile.html",
        profile=profile
    )


# ==========================================
# PUBLIC CHAMBER DETAILS
# ==========================================

@chamber_panel.route("/view/<int:chamber_id>")
def chamber_details(chamber_id):

    chamber = Chamber.query.get_or_404(chamber_id)

    profile = ChamberProfile.query.filter_by(
        chamber_id=chamber_id
    ).first()

    doctors = Doctor.query.filter_by(
        chamber_id=chamber_id
    ).all()

    return render_template(
        "chamber/chamber_details.html",
        chamber=chamber,
        profile=profile,
        doctors=doctors
    )

# ==========================================
# PUBLIC DOCTOR DETAILS
# ==========================================

@chamber_panel.route(
    "/doctor/view/<int:doctor_id>"
)
def doctor_details(doctor_id):

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    doctor.views += 1
    db.session.commit()

    return render_template(
        "doctor/doctor_details.html",
        doctor=doctor
    )



# ==========================================
# DOCTORS
# ==========================================

@chamber_panel.route("/doctors")
def doctors():

    chamber_id = session.get("chamber_id")

    doctors = Doctor.query.filter_by(
        chamber_id=chamber_id
    ).all()

    return render_template(
        "chamber/doctors.html",
        doctors=doctors
    )


# ==========================================
# ADD DOCTOR
# ==========================================

@chamber_panel.route(
    "/doctor/add",
    methods=["GET", "POST"]
)
def add_doctor():

    chamber_id = session.get("chamber_id")

    if request.method == "POST":

        doctor = Doctor(

            chamber_id=chamber_id,

            name=request.form.get("name"),

            degree=request.form.get(
                "degree"
            ),

            specialization=request.form.get(
                "specialization"
            ),

            hospital=request.form.get(
                "hospital"
            ),

            experience=request.form.get(
                "experience"
            ),

            about=request.form.get(
                "about"
            )
        )

        db.session.add(doctor)
        db.session.commit()

        flash(
            "Doctor added successfully",
            "success"
        )

        return redirect(
            "/chamber/doctors"
        )

    return render_template(
        "chamber/add_doctor.html"
    )


# ==========================================
# EDIT DOCTOR
# ==========================================

@chamber_panel.route(
    "/doctor/<int:doctor_id>/edit",
    methods=["GET", "POST"]
)
def edit_doctor(doctor_id):

    chamber_id = session.get(
        "chamber_id"
    )

    doctor = Doctor.query.filter_by(
        id=doctor_id,
        chamber_id=chamber_id
    ).first_or_404()

    if request.method == "POST":

        doctor.name = request.form.get(
            "name"
        )

        doctor.degree = request.form.get(
            "degree"
        )

        doctor.specialization = request.form.get(
            "specialization"
        )

        doctor.hospital = request.form.get(
            "hospital"
        )

        doctor.experience = request.form.get(
            "experience"
        )

        doctor.about = request.form.get(
            "about"
        )

        db.session.commit()

        flash(
            "Doctor updated successfully",
            "success"
        )

        return redirect(
            "/chamber/doctors"
        )

    return render_template(
        "chamber/edit_doctor.html",
        doctor=doctor
    )


# ==========================================
# DELETE DOCTOR
# ==========================================

@chamber_panel.route(
    "/doctor/<int:doctor_id>/delete"
)
def delete_doctor(doctor_id):

    chamber_id = session.get(
        "chamber_id"
    )

    doctor = Doctor.query.filter_by(
        id=doctor_id,
        chamber_id=chamber_id
    ).first_or_404()

    db.session.delete(doctor)
    db.session.commit()

    return redirect(
        "/chamber/doctors"
    )


# ==========================================
# APPOINTMENTS
# ==========================================

@chamber_panel.route("/appointments")
def appointments():

    chamber_id = session.get(
        "chamber_id"
    )

    appointments = Appointment.query.filter_by(
        chamber_id=chamber_id
    ).order_by(
        Appointment.id.desc()
    ).all()

    return render_template(
        "chamber/appointments.html",
        appointments=appointments
    )


# ==========================================
# UPDATE APPOINTMENT
# ==========================================

@chamber_panel.route(
    "/appointment/<int:appointment_id>/<status>"
)
def update_appointment(
    appointment_id,
    status
):

    chamber_id = session.get(
        "chamber_id"
    )

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        chamber_id=chamber_id
    ).first_or_404()

    appointment.status = status

    db.session.commit()

    return redirect(
        "/chamber/appointments"
  )

@chamber_panel.route("/chambers")
def chambers():

    chambers = ChamberProfile.query.filter_by(
        status="active"
    ).all()

    return render_template(
        "chamber/chambers.html",
        chambers=chambers
    )


@chamber_panel.route(
    "/rate/<int:chamber_id>",
    methods=["POST"]
)
def rate_chamber(chamber_id):

    try:
        rating_value = int(
            request.form.get("rating", 0)
        )

        if rating_value not in [1, 2, 3, 4, 5]:
            flash("Invalid rating.", "danger")
            return redirect(
                f"/chamber/view/{chamber_id}"
            )

        ip = request.remote_addr

        existing = ChamberRating.query.filter_by(
            chamber_id=chamber_id,
            ip_address=ip
        ).first()

        if existing:
            existing.rating = rating_value
        else:
            db.session.add(
                ChamberRating(
                    chamber_id=chamber_id,
                    rating=rating_value,
                    ip_address=ip
                )
            )

        db.session.commit()

        flash(
            "Rating submitted successfully.",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash(
            "Something went wrong.",
            "danger"
        )

    return redirect(
        f"/chamber/view/{chamber_id}"
    )
