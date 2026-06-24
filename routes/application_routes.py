from flask import Blueprint, request, redirect, flash, session, render_template
from datetime import datetime, UTC
from models.user import User
from models.work_model import Work
from models.work_application import WorkApplication
from extensions import db
from utils.notification_helper import send_notification


application_bp = Blueprint('application', __name__)

# =================================================
# 🟢 APPLY FORM PAGE (GET)
# =================================================
@application_bp.route('/apply_work/<int:work_id>', methods=['GET'])
def apply_form(work_id):

    if not session.get("user_id"):
        flash("Please login first", "danger")
        return redirect('/auth/login')

    work = Work.query.get_or_404(work_id)

    return render_template("apply_form.html", work=work)


# =================================================
# 🟢 APPLY SUBMIT (POST)
# =================================================
@application_bp.route(
    "/apply_work/<int:work_id>",
    methods=["POST"]
)
def apply_work(work_id):

    user_id = session.get("user_id")

    if not user_id:
        flash(
            "Please login first",
            "danger"
        )
        return redirect(
            "/auth/login"
        )

    work = Work.query.get_or_404(
        work_id
    )

    existing = WorkApplication.query.filter_by(
        work_id=work_id,
        user_id=user_id
    ).first()

    if existing:
        flash(
            "Already applied for this work",
            "info"
        )
        return redirect(
            "/works"
        )

    try:

        experience_years = int(
            request.form.get(
                "experience_years",
                0
            ) or 0
        )

        expected_salary = int(
            request.form.get(
                "expected_salary",
                0
            ) or 0
        )

        application = WorkApplication(

            work_id=work_id,

            user_id=user_id,

            name=session.get(
                "name"
            ) or "Unknown",

            phone=session.get(
                "phone"
            ) or "N/A",

            address=session.get(
                "address"
            ) or "N/A",

            message=request.form.get(
                "message",
                ""
            ).strip(),

            experience_years=experience_years,

            expected_salary=expected_salary,

            applied_ip=request.remote_addr
        )

        db.session.add(
            application
        )

        db.session.commit()

        send_notification(

            user_id=user_id,

            title="Application Submitted",

            message=(
                "Your application has been "
                "submitted successfully."
            ),

            type="application",

            icon="send",

            priority="normal",

            action_url="/my_applications"
        )

        flash(
            "Application submitted successfully",
            "success"
        )

        return redirect(
            "/works"
        )

    except ValueError:

        db.session.rollback()

        flash(
            "Invalid salary or experience value",
            "danger"
        )

        return redirect(
            f"/apply_work/{work_id}"
        )

    except Exception as e:

        db.session.rollback()

        print(
            f"APPLICATION ERROR: {e}"
        )

        flash(
            "Application submit failed",
            "danger"
        )

        return redirect(
            f"/apply_work/{work_id}"
        )
# =================================================
# 📋 OWNER - ALL APPLICATIONS
# =================================================
@application_bp.route('/owner/applications')
def owner_applications():

    owner_id = session.get(
        "user_id"
    )

    if not owner_id:

        flash(
            "Please login first",
            "danger"
        )

        return redirect(
            "/auth/login"
        )

    status = request.args.get(
        "status"
    )

    query = WorkApplication.query.filter(
        WorkApplication.is_deleted == False
    )

    if status and status != "all":

        query = query.filter(
            WorkApplication.status == status
        )

    applications = query.order_by(
        WorkApplication.id.desc()
    ).all()

    return render_template(
        "owner_applications.html",
        applications=applications,
        status=status
    )
# =================================================
# 👁 MARK SEEN
# =================================================
@application_bp.route(
    "/owner/application/seen/<int:id>",
    methods=["POST"]
)
def mark_seen(id):

    app = WorkApplication.query.get_or_404(
        id
    )

    app.is_seen = True

    db.session.commit()

    return redirect(
        "/owner/applications"
    )


# =================================================
# ✔ APPROVE
# =================================================
@application_bp.route(
    "/owner/application/approve/<int:id>",
    methods=["POST"]
)
def approve_application(id):

    app = WorkApplication.query.get_or_404(
        id
    )

    app.status = "approved"

    app.is_shortlisted = True

    app.updated_at = datetime.now(
        UTC
    )

    db.session.commit()

    send_notification(
        user_id=app.user_id,
        title="Application Approved",
        message="Your work application has been approved.",
        type="approve",
        icon="check-circle",
        priority="high"
    )

    flash(
        "Approved",
        "success"
    )

    return redirect(
        "/owner/applications"
    )

# =================================================
# ❌ REJECT
# =================================================
@application_bp.route(
    "/owner/application/reject/<int:id>",
    methods=["POST"]
)
def reject_application(id):

    app = WorkApplication.query.get_or_404(
        id
    )

    app.status = "rejected"

    app.updated_at = datetime.now(
        UTC
    )

    db.session.commit()

    send_notification(
        user_id=app.user_id,
        title="Application Rejected",
        message="Sorry, your application was rejected.",
        type="reject",
        icon="x-circle",
        priority="high"
    )

    flash(
        "Rejected",
        "warning"
    )

    return redirect(
        "/owner/applications"
    )

# =================================================
# 🗑 DELETE (SOFT)
# =================================================
@application_bp.route(
    "/owner/application/delete/<int:id>",
    methods=["POST"]
)
def delete_application(id):
    send_notification(
        user_id=app.user_id,
        title="Application Cancelled",
        message="Your application has been cancelled.",
        type="cancel",
        icon="trash",
        priority="normal",
        action_url="/my_applications"
    )

    app = WorkApplication.query.get_or_404(
        id
    )

    app.is_deleted = True

    app.status = "cancelled"

    app.updated_at = datetime.now(
        UTC
    )

    db.session.commit()

    flash(
        "Deleted",
        "danger"
    )

    return redirect(
        "/owner/applications"
    )

# =================================================
# 📄 DETAILS
# =================================================
@application_bp.route('/owner/application/<int:id>')
def application_details(id):
    
    app = WorkApplication.query.get_or_404(id)

    return render_template(
        "application_details.html",
        app=app
    )

@application_bp.route('/my_applications')
def my_applications():

    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "danger")
        return redirect('/auth/login')

    apps = WorkApplication.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).order_by(WorkApplication.id.desc()).all()

    return render_template("my_applications.html", apps=apps)

# =================================================
# 🛡 ADMIN - CONTROL USERS APPLICATIONS
# =================================================
@application_bp.route('/admin/applications')
def admin_applications():

    admin_id = session.get("user_id")

    if not admin_id:
        flash("Please login first", "danger")
        return redirect('/auth/login')

    status = request.args.get("status")

    query = WorkApplication.query.join(User).filter(
        User.controller_id == admin_id,
        WorkApplication.is_deleted == False
    )

    # STATUS FILTER
    if status and status != "all":
        query = query.filter(
            WorkApplication.status == status
        )

    applications = query.order_by(
        WorkApplication.id.desc()
    ).all()

    return render_template(
        "owner_applications.html",
        applications=applications,
        status=status
    )


# =================================================
# ✔ ADMIN APPROVE
# =================================================
@application_bp.route(
    "/admin/application/approve/<int:id>",
    methods=["POST"]
)
def admin_approve_application(id):

    admin_id = session.get("user_id")

    if not admin_id:
        flash("Please login first", "danger")
        return redirect("/auth/login")

    app = WorkApplication.query.join(User).filter(
        WorkApplication.id == id,
        User.controller_id == admin_id
    ).first_or_404()

    app.status = "approved"
    app.is_shortlisted = True
    app.updated_at = datetime.now(UTC)

    db.session.commit()

    # 🔔 Notification
    send_notification(
        user_id=app.user_id,
        title="Application Approved",
        message="Congratulations! Your application has been approved.",
        type="approve",
        icon="check-circle",
        priority="high",
        action_url="/my_applications"
    )

    flash(
        "Application Approved",
        "success"
    )

    return redirect(
        "/admin/applications"
    )

# =================================================
# ❌ ADMIN REJECT
# =================================================
@application_bp.route(
    "/admin/application/reject/<int:id>",
    methods=["POST"]
)
def admin_reject_application(id):

    admin_id = session.get("user_id")

    if not admin_id:
        flash(
            "Please login first",
            "danger"
        )
        return redirect(
            "/auth/login"
        )

    app = WorkApplication.query.join(
        User
    ).filter(
        WorkApplication.id == id,
        User.controller_id == admin_id
    ).first_or_404()

    app.status = "rejected"

    app.updated_at = datetime.now(
        UTC
    )

    db.session.commit()

    send_notification(
        user_id=app.user_id,
        title="Application Rejected",
        action_url="/my_applications",
        message="Sorry, your application was rejected.",
        type="reject",
        icon="x-circle",
        priority="high"
    )

    flash(
        "Application Rejected",
        "warning"
    )

    return redirect(
        "/admin/applications"
    )


# =================================================
# 🗑 ADMIN DELETE
# =================================================
@application_bp.route(
    "/admin/application/delete/<int:id>",
    methods=["POST"]
)
def admin_delete_application(id):

    admin_id = session.get("user_id")

    if not admin_id:
        flash(
            "Please login first",
            "danger"
        )
        return redirect(
            "/auth/login"
        )

    app = WorkApplication.query.join(
        User
    ).filter(
        WorkApplication.id == id,
        User.controller_id == admin_id
    ).first_or_404()

    app.is_deleted = True

    app.status = "cancelled"

    app.updated_at = datetime.now(
        UTC
    )

    db.session.commit()
    send_notification(
        user_id=app.user_id,
        title="Application Cancelled",
        action_url="/my_applications",
        message="Your application has been cancelled.",
        type="cancel",
        icon="trash",
        priority="normal"
    )

    flash(
        "Application Deleted",
        "danger"
    )

    return redirect(
        "/admin/applications"
    )
