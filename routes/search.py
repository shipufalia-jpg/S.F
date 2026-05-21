from flask import Blueprint, request, render_template, session
from services.search_service import (
    search_users,
    search_workers,
    search_bookings,
    search_works
)

search = Blueprint('search', __name__)


# ================= ROLE CHECK =================
def can_access_search():
    return session.get('role') in ["owner", "admin", "super_admin"]


# =================================================
# 👤 USER SEARCH ROUTE
# =================================================
@search.route('/search/users')
def users_search():

    if not can_access_search():
        return "Unauthorized"

    query = request.args.get('q')
    area = request.args.get('area')
    skill = request.args.get('skill')

    users = search_users(query=query, area=area, skill=skill)

    return render_template("search_users.html", users=users)


# =================================================
# 👷 WORKER SEARCH ROUTE
# =================================================
@search.route('/search/workers')
def workers_search():

    if not can_access_search():
        return "Unauthorized"

    query = request.args.get('q')
    area = request.args.get('area')
    skill = request.args.get('skill')

    workers = search_workers(query=query, area=area, skill=skill)

    return render_template("search_workers.html", workers=workers)


# =================================================
# 📦 BOOKING SEARCH ROUTE
# =================================================
@search.route('/search/bookings')
def bookings_search():

    if not can_access_search():
        return "Unauthorized"

    query = request.args.get('q')
    status = request.args.get('status')

    bookings = search_bookings(query=query, status=status)

    return render_template("search_bookings.html", bookings=bookings)


# =================================================
# 🧰 WORK SEARCH ROUTE
# =================================================
@search.route('/search/works')
def works_search():

    if not can_access_search():
        return "Unauthorized"

    query = request.args.get('q')
    area = request.args.get('area')

    works = search_works(query=query, area=area)

    return render_template("search_works.html", works=works)