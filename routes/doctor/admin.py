from . import doctor_bp
from flask import request, render_template, redirect
from models.doctor import Doctor


@doctor_bp.route("/admin/create", methods=["GET", "POST"])
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
            cover_photo=request.form.get("cover_photo")
        )

        db.session.add(doctor)
        db.session.commit()

        return redirect("/doctors")

    return render_template("doctor/create.html")
