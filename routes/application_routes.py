from flask import Blueprint, request, redirect, flash, session, render_template
from datetime import datetime

from models.work_model import Work
from models.work_application import WorkApplication
from extensions import db

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
@application_bp.route('/apply_work/<int:work_id>', methods=['POST'])
def apply_work(work_id):

    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "danger")
        return redirect('/auth/login')

    work = Work.query.get_or_404(work_id)

    # duplicate check
    existing = WorkApplication.query.filter_by(
        work_id=work_id,
        user_id=user_id
    ).first()

    if existing:
        flash("Already applied for this work", "info")
        return redirect('/works')

    application = WorkApplication(
        work_id=work_id,
        user_id=user_id,

        name=session.get("name"),
        phone=session.get("phone"),
        address=session.get("address"),

        message=request.form.get("message"),
        experience_years=request.form.get("experience_years") or 0,
        expected_salary=request.form.get("expected_salary"),

        applied_ip=request.remote_addr
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully", "success")
    return redirect('/works')


# =================================================
# 📋 OWNER - ALL APPLICATIONS
# =================================================
@application_bp.route('/owner/applications')
def owner_applications():

    status = request.args.get("status")

    query = WorkApplication.query.filter_by(is_deleted=False)

    if status and status != "all":
        query = query.filter_by(status=status)

    applications = query.order_by(WorkApplication.id.desc()).all()

    return render_template(
        "owner_applications.html",
        applications=applications,
        status=status
    )


# =================================================
# 👁 MARK SEEN
# =================================================
@application_bp.route('/owner/application/seen/<int:id>')
def mark_seen(id):

    app = WorkApplication.query.get_or_404(id)
    app.is_seen = True
    db.session.commit()

    return redirect('/owner/applications')


# =================================================
# ✔ APPROVE
# =================================================
@application_bp.route('/owner/application/approve/<int:id>')
def approve_application(id):

    app = WorkApplication.query.get_or_404(id)

    app.status = "approved"
    app.is_shortlisted = True
    app.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Approved", "success")
    return redirect('/owner/applications')


# =================================================
# ❌ REJECT
# =================================================
@application_bp.route('/owner/application/reject/<int:id>')
def reject_application(id):

    app = WorkApplication.query.get_or_404(id)

    app.status = "rejected"
    app.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Rejected", "warning")
    return redirect('/owner/applications')


# =================================================
# 🗑 DELETE (SOFT)
# =================================================
@application_bp.route('/owner/application/delete/<int:id>')
def delete_application(id):

    app = WorkApplication.query.get_or_404(id)

    app.is_deleted = True
    app.status = "cancelled"

    db.session.commit()

    flash("Deleted", "danger")
    return redirect('/owner/applications')


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
