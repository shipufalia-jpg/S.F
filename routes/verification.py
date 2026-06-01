from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    session
)

from datetime import datetime, timedelta

from extensions import db
from models.user import User
from models.verification_request import VerificationRequest


from decorators.owner_required import owner_required


verification = Blueprint(
    "verification",
    __name__,
    url_prefix="/verification"
)


# =========================
# USER REQUEST VERIFICATION
# =========================

@verification.route("/request", methods=["GET", "POST"])
def request_verification():

    user = User.query.get_or_404(
        session["user_id"]
    )

    if user.is_verified:
        return "Your profile is already verified."

    existing_request = VerificationRequest.query.filter_by(
        user_id=user.id,
        status="pending"
    ).first()

    if existing_request:
        return "Verification request already pending."

    if request.method == "POST":

        plan_months = int(
            request.form.get("plan_months", 1)
        )

        if plan_months not in [1, 6]:
            return "Invalid verification plan."

        amount = 100

        if plan_months == 6:
            amount = 500

        verification_request = VerificationRequest(
            user_id=user.id,
            plan_months=plan_months,
            amount=amount,
            payment_status="pending",
            status="pending"
        )

        db.session.add(
            verification_request
        )

        db.session.commit()

        return redirect(
            "/verification/my-requests"
        )

    return render_template(
        "verification/request.html",
        user=user
    )


# =========================
# USER REQUEST HISTORY
# =========================

@verification.route("/my-requests")
def my_requests():

    requests = VerificationRequest.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        VerificationRequest.created_at.desc()
    ).all()

    return render_template(
        "verification/my_requests.html",
        requests=requests
    )


# =========================
# ADMIN PANEL
# =========================

@verification.route("/admin/requests")
@owner_required
def admin_requests():

    requests = VerificationRequest.query.order_by(
        VerificationRequest.created_at.desc()
    ).all()

    pending_count = sum(
        1 for r in requests
        if r.status == "pending"
    )

    approved_count = sum(
        1 for r in requests
        if r.status == "approved"
    )

    rejected_count = sum(
        1 for r in requests
        if r.status == "rejected"
    )

    return render_template(
        "owner/verification_requests.html",
        requests=requests,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count
    )


# =========================
# APPROVE REQUEST
# =========================

@verification.route(
    "/admin/approve/<int:request_id>"
)
@owner_required
def approve_verification(request_id):

    verification_request = (
        VerificationRequest.query.get_or_404(
            request_id
        )
    )

    if verification_request.status != "pending":
        return redirect(
            "/verification/admin/requests"
        )

    user = User.query.get_or_404(
        verification_request.user_id
    )

    days = 30

    if verification_request.plan_months == 6:
        days = 180

    user.is_verified = True

    user.verification_expiry = (
        datetime.utcnow()
        + timedelta(days=days)
    )

    verification_request.status = "approved"

    verification_request.payment_status = "paid"

    verification_request.reviewed_at = (
        datetime.utcnow()
    )

    db.session.commit()

    return redirect(
        "/verification/admin/requests"
    )


# =========================
# REJECT REQUEST
# =========================

@verification.route(
    "/admin/reject/<int:request_id>",
    methods=["POST"]
)
@owner_required
def reject_verification(request_id):

    verification_request = (
        VerificationRequest.query.get_or_404(
            request_id
        )
    )

    reason = request.form.get(
        "reason",
        "Rejected by admin"
    )

    verification_request.status = "rejected"

    verification_request.rejection_reason = (
        reason
    )

    verification_request.reviewed_at = (
        datetime.utcnow()
    )

    db.session.commit()

    return redirect(
        "/verification/admin/requests"
    )


# =========================
# REMOVE VERIFICATION
# =========================

@verification.route(
    "/admin/remove/<int:user_id>"
)
@owner_required
def remove_verification(user_id):

    user = User.query.get_or_404(
        user_id
    )

    user.is_verified = False

    user.verification_expiry = None

    db.session.commit()

    return redirect(
        "/verification/admin/requests"
  )
