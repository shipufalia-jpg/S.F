from models.user import User

def assign_control(user, referrer=None):

    # ================= NO REFERRAL =================
    if not referrer:

        owner = User.query.filter_by(role="owner").first()

        if owner:
            user.controller_id = owner.id

        return


    # ================= OWNER / ADMIN / SUPER ADMIN =================
    if referrer.role in ["owner", "admin", "super_admin"]:

        user.controller_id = referrer.id
        return


    # ================= USER REFERRAL =================
    if referrer.role == "user":

        if referrer.controller_id:
            user.controller_id = referrer.controller_id

        else:

            owner = User.query.filter_by(role="owner").first()

            if owner:
                user.controller_id = owner.id

        return
      
