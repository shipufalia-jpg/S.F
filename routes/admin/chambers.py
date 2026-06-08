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

        admin = User.query.get(admin_id)

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

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

        chamber = Chamber(

            name=request.form.get("name"),

            username=username,

            phone=request.form.get("phone"),

            address=request.form.get(
                "address"
            ),

            created_by_admin_id=admin_id,

            controller_admin_id=admin_id,

            super_admin_id=admin.controller_id,

            owner_id=None
        )

        chamber.set_password(password)

        db.session.add(chamber)
        db.session.commit()

        flash(
            "Chamber created successfully.",
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
