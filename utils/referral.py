from models.user import User
from models.notification import Notification
from models.referral_earning import ReferralEarning

from extensions import db


# =====================================================
# GIVE REFERRAL BONUS
# =====================================================

def give_referral_bonus(user, amount=50):

    try:

        # ================= CHECK REFERRAL =================

        if not user.referred_by:
            return

        # ================= FIND REFERRER =================

        referrer = User.query.get(
            user.referred_by
        )

        if not referrer:
            return

        # ================= SELF REFERRAL BLOCK =================

        if referrer.id == user.id:
            return

        # ================= ONE TIME BONUS =================

        existing_bonus = ReferralEarning.query.filter_by(
            referred_user_id=user.id
        ).first()

        if existing_bonus:
            return

        # ================= WALLET UPDATE =================

        referrer.wallet_balance = (
            referrer.wallet_balance or 0
        ) + amount

        referrer.total_earnings = (
            referrer.total_earnings or 0
        ) + amount

        # ================= SAVE EARNING =================

        earning = ReferralEarning(
            referrer_id=referrer.id,
            referred_user_id=user.id,
            amount=amount,
            reason="Referral Bonus"
        )

        db.session.add(earning)

        # ================= NOTIFICATION =================

        notification = Notification(
            user_id=referrer.id,
            title="Referral Bonus",
            message=f"You earned ₹{amount} from {user.name}"
        )

        db.session.add(notification)

        # ================= COMMIT =================

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        print("Referral Bonus Error:", e)
