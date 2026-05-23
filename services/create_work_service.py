from models.work_model import Work
from extensions import db


def create_work(data, user_id):

    try:

        # ================= VALIDATION =================
        if not data.get("title") or not data.get("salary"):
            raise ValueError("Title and Salary are required")

        # ================= CREATE WORK =================
        work = Work(
            title=data.get("title"),
            description=data.get("description", "No description"),
            workers=data.get("workers"),
            salary=data.get("salary"),
            date=data.get("date"),
            time=data.get("time"),
            mobile=data.get('phone'),
            phone=data.get("phone"),
            user_id=user_id,
            status="pending"
        )

        # ================= SAVE =================
        db.session.add(work)
        db.session.commit()

        return work

    except Exception as e:
        db.session.rollback()
        print("Create Work Error:", str(e))
        return None
