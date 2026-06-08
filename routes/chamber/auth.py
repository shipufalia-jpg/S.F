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


chamber = Blueprint(
    "chamber",
    __name__,
    url_prefix="/chamber"
)


# ==========================================
# CHAMBER LOGIN
# ==========================================

@chamber.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":
        return render_template(
            "chamber/login.html"
        )

    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )

    chamber_account = Chamber.query.filter_by(
        username=username
    ).first()

    if not chamber_account:

        flash(
            "Invalid username.",
            "danger"
        )

        return redirect(
            url_for("chamber.login")
        )

    if chamber_account.status == "blocked":

        flash(
            "This chamber is blocked by owner.",
            "danger"
        )

        return redirect(
            url_for("chamber.login")
        )

    if not chamber_account.check_password(
        password
    ):

        flash(
            "Wrong password.",
            "danger"
        )

        return redirect(
            url_for("chamber.login")
        )

    session["chamber_id"] = chamber_account.id
    session["chamber_name"] = chamber_account.name

    chamber_account.last_login = db.func.now()

    db.session.commit()

    return redirect(
        "/chamber/dashboard"
    )


# ==========================================
# CHAMBER LOGOUT
# ==========================================

@chamber.route("/logout")
def logout():

    session.pop(
        "chamber_id",
        None
    )

    session.pop(
        "chamber_name",
        None
    )

    return redirect(
        url_for("chamber.login")
    )


# ==========================================
# CHANGE PASSWORD
# ==========================================

@chamber.route(
    "/change-password",
    methods=["GET", "POST"]
)
def change_password():

    chamber_id = session.get(
        "chamber_id"
    )

    if not chamber_id:

        return redirect(
            url_for("chamber.login")
        )

    chamber_account = Chamber.query.get_or_404(
        chamber_id
    )

    if request.method == "POST":

        current_password = request.form.get(
            "current_password"
        )

        new_password = request.form.get(
            "new_password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        if not chamber_account.check_password(
            current_password
        ):

            flash(
                "Current password incorrect.",
                "danger"
            )

            return redirect(
                url_for(
                    "chamber.change_password"
                )
            )

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for(
                    "chamber.change_password"
                )
            )

        chamber_account.set_password(
            new_password
        )

        db.session.commit()

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            "/chamber/dashboard"
        )

    return render_template(
        "chamber/change_password.html"
        )
