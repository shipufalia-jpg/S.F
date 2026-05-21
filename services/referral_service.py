def assign_control(new_user, referrer):

    # ================= DIRECT SIGNUP =================
    if not referrer:
        new_user.controller_id = 1

        # 🔥 role অনুযায়ী status
        if new_user.role == "user":
            new_user.status = "active"   # no approval
        else:
            new_user.status = "pending"  # owner approve করবে

        return

    # ================= SUPER ADMIN REFERRAL =================
    if referrer.role == "super_admin":
        new_user.role = "admin"
        new_user.controller_id = referrer.id
        new_user.status = "pending"   # super admin approve করবে

    # ================= ADMIN REFERRAL =================
    elif referrer.role == "admin":
        new_user.role = "user"
        new_user.controller_id = referrer.id
        new_user.status = "active"

    # ================= USER REFERRAL =================
    elif referrer.role == "user":
        new_user.role = "user"
        new_user.controller_id = referrer.controller_id
        new_user.status = "active"

    new_user.referred_by = referrer.id