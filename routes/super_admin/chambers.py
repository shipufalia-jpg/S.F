from flask import (
    Blueprint,
    render_template,
    session
)

from models.chamber import Chamber
from models.user import User


super_chambers = Blueprint(
    "super_chambers",
    __name__,
    url_prefix="/super"
)


# ==========================================
# ALL NETWORK CHAMBERS
# ==========================================

@super_chambers.route("/chambers")
def chambers():

    super_admin_id = session.get(
        "user_id"
    )

    chambers = Chamber.query.filter_by(
        super_admin_id=super_admin_id
    ).order_by(
        Chamber.id.desc()
    ).all()

    return render_template(
        "super_admin/chambers.html",
        chambers=chambers
    )


# ==========================================
# CHAMBER DETAILS
# ==========================================

@super_chambers.route(
    "/chamber/<int:chamber_id>"
)
def chamber_details(chamber_id):

    super_admin_id = session.get(
        "user_id"
    )

    chamber = Chamber.query.filter_by(
        id=chamber_id,
        super_admin_id=super_admin_id
    ).first_or_404()

    return render_template(
        "super_admin/chamber_details.html",
        chamber=chamber
    )


# ==========================================
# NETWORK SUMMARY
# ==========================================

@super_chambers.route("/dashboard")
def dashboard():

    super_admin_id = session.get(
        "user_id"
    )

    chambers = Chamber.query.filter_by(
        super_admin_id=super_admin_id
    ).all()

    total_chambers = len(chambers)

    total_admins = User.query.filter_by(
        controller_id=super_admin_id,
        role="admin"
    ).count()

    return render_template(
        "super_admin/dashboard.html",
        total_chambers=total_chambers,
        total_admins=total_admins,
        chambers=chambers
)
