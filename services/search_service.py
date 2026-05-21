from models.user import User
from models.booking import Booking
from models.work import Work


# ================= USER SEARCH =================
def search_users(query=None, area=None, skill=None):

    q = User.query.filter(User.is_deleted == False)

    if query:
        q = q.filter(User.name.ilike(f"%{query}%"))

    if area:
        q = q.filter(User.area.ilike(f"%{area}%"))

    if skill:
        q = q.filter(User.skill.ilike(f"%{skill}%"))

    return q.order_by(User.id.desc()).all()


# ================= WORKER SEARCH =================
def search_workers(query=None, area=None, skill=None):

    q = User.query.filter(
        User.role == "worker",
        User.is_deleted == False,
        User.status == "active"
    )

    if query:
        q = q.filter(User.name.ilike(f"%{query}%"))

    if area:
        q = q.filter(User.area.ilike(f"%{area}%"))

    if skill:
        q = q.filter(User.skill.ilike(f"%{skill}%"))

    return q.order_by(User.id.desc()).all()


# ================= BOOKING SEARCH =================
def search_bookings(query=None, status=None):

    q = Booking.query.filter(Booking.is_deleted == False)

    if query:
        q = q.join(User).filter(User.name.ilike(f"%{query}%"))

    if status:
        q = q.filter(Booking.status == status)

    return q.order_by(Booking.id.desc()).all()


# ================= WORK SEARCH =================
def search_works(query=None, area=None):

    q = Work.query.filter(Work.is_deleted == False)

    if query:
        q = q.filter(Work.title.ilike(f"%{query}%"))

    if area:
        q = q.filter(Work.phone.ilike(f"%{area}%"))  # future: replace with location field

    return q.order_by(Work.id.desc()).all()