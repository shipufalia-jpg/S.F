import uuid

from extensions import db

from models.user import User
from models.transaction import Transaction

from utils.notification import send_notification


# =====================================================
# CONFIG
# =====================================================

MIN_WITHDRAW_AMOUNT = 100


# =====================================================
# GENERATE TRANSACTION ID
# =====================================================

def generate_transaction_id():

    return str(uuid.uuid4()).replace("-", "")[:12]


# =====================================================
# GET USER BALANCE
# =====================================================

def get_user_balance(user):

    if not user:
        return 0.0

    balance = user.wallet_balance or 0

    if balance < 0:
        return 0.0

    return round(float(balance), 2)


# =====================================================
# ADD MONEY
# =====================================================

def add_money(user, amount, reason="Wallet Credit"):

    try:

        if not user:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        user.wallet_balance = float(user.wallet_balance or 0) + amount
        user.total_earnings = float(user.total_earnings or 0) + amount

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        transaction = Transaction(

            transaction_id=generate_transaction_id(),
            user_id=user.id,
            amount=amount,
            type="credit",
            status="success",
            reason=reason

        )

        db.session.add(transaction)
        db.session.flush()

        send_notification(
            user_id=user.id,
            title="Wallet Credited",
            message=f"₹{amount} added to your wallet",
            type="payment",
            icon="money",
            action_url="/wallet",
            priority="normal"
        )

        db.session.commit()
        return True

    except Exception as e:

        db.session.rollback()
        print("Add Money Error:", e)
        return False


# =====================================================
# DEDUCT MONEY
# =====================================================

def deduct_money(user, amount, reason="Wallet Debit"):

    try:

        if not user:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        current_balance = float(user.wallet_balance or 0)

        if current_balance < amount:
            return False

        user.wallet_balance = current_balance - amount

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        transaction = Transaction(

            transaction_id=generate_transaction_id(),
            user_id=user.id,
            amount=amount,
            type="debit",
            status="success",
            reason=reason

        )

        db.session.add(transaction)
        db.session.flush()

        send_notification(
            user_id=user.id,
            title="Wallet Debited",
            message=f"₹{amount} deducted from wallet",
            type="payment",
            icon="money",
            action_url="/wallet",
            priority="normal"
        )

        db.session.commit()
        return True

    except Exception as e:

        db.session.rollback()
        print("Deduct Money Error:", e)
        return False


# =====================================================
# TRANSFER MONEY
# =====================================================

def transfer_money(sender, receiver, amount):

    try:

        if not sender or not receiver:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        if sender.id == receiver.id:
            return False

        sender_balance = float(sender.wallet_balance or 0)

        if sender_balance < amount:
            return False

        sender.wallet_balance = sender_balance - amount
        receiver.wallet_balance = float(receiver.wallet_balance or 0) + amount

        if sender.wallet_balance < 0:
            sender.wallet_balance = 0

        sender_tx = Transaction(
            transaction_id=generate_transaction_id(),
            user_id=sender.id,
            amount=amount,
            type="transfer_out",
            status="success",
            reason=f"Transfer to {receiver.name}"
        )

        receiver_tx = Transaction(
            transaction_id=generate_transaction_id(),
            user_id=receiver.id,
            amount=amount,
            type="transfer_in",
            status="success",
            reason=f"Received from {sender.name}"
        )

        db.session.add(sender_tx)
        db.session.add(receiver_tx)
        db.session.flush()

        send_notification(
            user_id=sender.id,
            title="Money Sent",
            message=f"₹{amount} sent to {receiver.name}",
            type="payment",
            icon="money",
            action_url="/wallet"
        )

        send_notification(
            user_id=receiver.id,
            title="Money Received",
            message=f"₹{amount} received from {sender.name}",
            type="payment",
            icon="money",
            action_url="/wallet"
        )

        db.session.commit()
        return True

    except Exception as e:

        db.session.rollback()
        print("Transfer Money Error:", e)
        return False


# =====================================================
# WITHDRAW MONEY
# =====================================================

def withdraw_money(user, amount):

    try:

        if not user:
            return False

        amount = float(amount)

        # ================= MINIMUM WITHDRAW RULE =================

        if amount < MIN_WITHDRAW_AMOUNT:
            return False

        balance = float(user.wallet_balance or 0)

        if balance < amount:
            return False

        user.wallet_balance = balance - amount

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        transaction = Transaction(

            transaction_id=generate_transaction_id(),
            user_id=user.id,
            amount=amount,
            type="withdraw",
            status="pending",
            reason="Wallet Withdraw"

        )

        db.session.add(transaction)
        db.session.flush()

        send_notification(
            user_id=user.id,
            title="Withdraw Requested",
            message=f"₹{amount} withdraw request submitted (Min ₹{MIN_WITHDRAW_AMOUNT})",
            type="payment",
            icon="money",
            action_url="/wallet",
            priority="high"
        )

        db.session.commit()
        return True

    except Exception as e:

        db.session.rollback()
        print("Withdraw Error:", e)
        return False
