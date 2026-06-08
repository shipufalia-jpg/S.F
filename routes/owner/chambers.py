from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from extensions import db

from models.user import User
from models.chamber import Chamber

from utils.decorators import owner_required


owner_chambers = Blueprint(
    "owner_chambers",
    __name__,
    url_prefix="/owner"
)


# ==========================================
# OWNER DASHBOARD
# ==========================================

@owner_chambers.route("/dashboard")
@owner_required
def dashboard():

    total_users = User.query.count()

    total_admins = User.query.filter_by(
        role="admin"
    ).count()

    total_super_admins = User.query.filter_by(
        role="super_admin"
    ).count()

    total_chambers = Chamber.query.count()

    active_chambers = Chamber.query.filter_by(
        status="active"
    ).count()

    blocked_chambers = Chamber.query.filter_by(
        status="blocked"
    ).count()

    return render_template(
        "owner/dashboard.html",
        total_users=total_users,
        total_admins=total_admins,
        total_super_admins=total_super_admins,
        total_chambers=total_chambers,
        active_chambers=active_chambers,
        blocked_chambers=blocked_chambers
    )


# ==========================================
# ALL CHAMBERS
# ==========================================

@owner_chambers.route("/chambers")
@owner_required
def chambers_list():

    chambers = Chamber.query.order_by(
        Chamber.id.desc()
    ).all()

    return render_template(
        "owner/chambers.html",
        chambers=chambers
    )


# ==========================================
# CHAMBER DETAILS
# ==========================================

@owner_chambers.route("/chamber/<int:chamber_id>")
@owner_required
def chamber_details(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    return render_template(
        "owner/chamber_details.html",
        chamber=chamber
    )


# ==========================================
# EDIT CHAMBER
# ==========================================

@owner_chambers.route(
    "/chamber/<int:chamber_id>/edit",
    methods=["GET", "POST"]
)
@owner_required
def edit_chamber(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    if request.method == "POST":

        chamber.name = request.form.get(
            "name",
            chamber.name
        )

        chamber.phone = request.form.get(
            "phone",
            chamber.phone
        )

        chamber.address = request.form.get(
            "address",
            chamber.address
        )

        db.session.commit()

        flash(
            "Chamber updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "owner_chambers.chamber_details",
                chamber_id=chamber.id
            )
        )

    return render_template(
        "owner/edit_chamber.html",
        chamber=chamber
    )


# ==========================================
# BLOCK CHAMBER
# ==========================================

@owner_chambers.route(
    "/chamber/<int:chamber_id>/block"
)
@owner_required
def block_chamber(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    chamber.status = "blocked"

    db.session.commit()

    flash(
        "Chamber blocked successfully.",
        "warning"
    )

    return redirect(
        url_for(
            "owner_chambers.chambers_list"
        )
    )


# ==========================================
# UNBLOCK CHAMBER
# ==========================================

@owner_chambers.route(
    "/chamber/<int:chamber_id>/unblock"
)
@owner_required
def unblock_chamber(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    chamber.status = "active"

    db.session.commit()

    flash(
        "Chamber activated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "owner_chambers.chambers_list"
        )
    )


# ==========================================
# DELETE CHAMBER
# ==========================================

@owner_chambers.route(
    "/chamber/<int:chamber_id>/delete"
)
@owner_required
def delete_chamber(chamber_id):

    chamber = Chamber.query.get_or_404(
        chamber_id
    )

    db.session.delete(chamber)

    db.session.commit()

    flash(
        "Chamber deleted successfully.",
        "danger"
    )

    return redirect(
        url_for(
            "owner_chambers.chambers_list"
        )
)
