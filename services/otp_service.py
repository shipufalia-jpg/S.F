import random
from datetime import datetime, timedelta

OTP_STORE = {}
OTP_EXPIRY_MINUTES = 5


def generate_otp(user_id):
    otp = str(random.randint(100000, 999999))

    OTP_STORE[user_id] = {
        "otp": otp,
        "time": datetime.utcnow()
    }

    return otp


def verify_otp(user_id, otp_input):
    data = OTP_STORE.get(user_id)

    if not data:
        return False

    # expiry check
    if datetime.utcnow() - data["time"] > timedelta(minutes=OTP_EXPIRY_MINUTES):
        OTP_STORE.pop(user_id, None)
        return False

    # match check
    if data["otp"] == otp_input:
        OTP_STORE.pop(user_id, None)
        return True

    return False
    