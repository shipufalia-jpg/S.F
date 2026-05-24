from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    flash,
    url_for
)

from flask import current_app
from sqlalchemy.orm import joinedload
from extensions import db
from models.work_model import Work
from models.work_application import WorkApplication
from services.create_work_service import create_work as create_work_service

work = Blueprint("work", __name__)


# =====================================================
# CREATE WORK
# =====================================================
@work.route('/user/post_work', methods=['GET', 'POST'])
def create_work_route():

    # LOGIN CHECK
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # SHOW PAGE
    if request.method == 'GET':
        return render_template("create_work.html")

    # FORM DATA
    data = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "workers": request.form.get("workers"),
        "salary": request.form.get("salary"),
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "phone": request.form.get("phone")
    }

    # VALIDATION
    if not data["title"] or not data["salary"]:
        flash("Title and Salary required")
        return redirect(url_for('work.create_work_route'))

    try:
        result = create_work_service(data, session["user_id"])

        if not result:
            flash("Failed to create work")
            return redirect(url_for('work.create_work_route'))

        flash("Work posted successfully")
        return redirect(url_for('work.work_list'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}")
        return redirect(url_for('work.create_work_route'))


# =====================================================
# ALL WORK LIST
# =====================================================
@work.route('/works')
def work_list():

    works = Work.query.filter_by(
        status="approved",
        is_deleted=False
    ).order_by(
        Work.id.desc()
    ).all()

    return render_template("work_list.html", works=works)



@work.route('/work/<int:id>', methods=['GET'])
def work_details(id):

    try:

        # =====================================================
        # GET ACTIVE WORK
        # =====================================================

        work_item = (
            Work.query
            .options(joinedload(Work.user))
            .filter(
                Work.id == id,
                Work.status == "approved",
                Work.is_deleted == False
            )
            .first()
        )

        # =====================================================
        # WORK NOT FOUND
        # =====================================================

        if not work_item:

            flash(
                "Work not found or unavailable",
                "danger"
            )

            return redirect(
                url_for('work.work_list')
            )

        # =====================================================
        # OWNER SAFE FETCH
        # =====================================================

        owner = getattr(work_item, "owner", None)

        # =====================================================
        # TOTAL APPLICATION COUNT
        # =====================================================

        total_applications = (
            WorkApplication.query
            .filter_by(work_id=work_item.id)
            .count()
        )

        # =====================================================
        # USER ALREADY APPLIED CHECK
        # =====================================================

        already_applied = False

        if session.get('user_id'):

            already_applied = (
                WorkApplication.query
                .filter_by(
                    user_id=session['user_id'],
                    work_id=work_item.id
                )
                .first()
                is not None
            )

        # =====================================================
        # RENDER TEMPLATE
        # =====================================================

        return render_template(

            "work_details.html",

            work=work_item,

            owner=owner,

            total_applications=total_applications,

            already_applied=already_applied
        )

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        current_app.logger.error(
            f"WORK DETAILS ERROR: {str(e)}"
        )

        flash(
            "Something went wrong",
            "danger"
        )

        return redirect(
            url_for('work.work_list')
        )
        
