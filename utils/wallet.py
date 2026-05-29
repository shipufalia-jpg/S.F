utils/wallet.py

import uuid

from extensions import db

from models.user import User
from models.transaction import Transaction

from utils.notification import send_notification


# =====================================================
# GENERATE TRANSACTION ID
# =====================================================

def generate_transaction_id():

    return str(uuid.uuid4()).replace("-", "")[:12]


# =====================================================
# ADD MONEY
# =====================================================

def add_money(
    user,
    amount,
    reason="Wallet Credit"
):

    try:

        # ================= VALIDATION =================

        if not user:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        # ================= UPDATE WALLET =================

        current_balance = float(
            user.wallet_balance or 0
        )

        current_earnings = float(
            user.total_earnings or 0
        )

        user.wallet_balance = (
            current_balance + amount
        )

        user.total_earnings = (
            current_earnings + amount
        )

        # ================= SAFETY =================

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        # ================= TRANSACTION =================

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

        # ================= NOTIFICATION =================

        send_notification(
            user_id=user.id,
            title="Wallet Credited",
            message=f"₹{amount} added to your wallet",
            type="payment",
            icon="money",
            action_url="/wallet",
            priority="normal"
        )

        # ================= COMMIT =================

        db.session.commit()

        return True

    except Exception as e:

        db.session.rollback()

        print("Add Money Error:", e)

        return False


# =====================================================
# DEDUCT MONEY
# =====================================================

def deduct_money(
    user,
    amount,
    reason="Wallet Debit"
):

    try:

        # ================= VALIDATION =================

        if not user:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        current_balance = float(
            user.wallet_balance or 0
        )

        if current_balance < amount:
            return False

        # ================= UPDATE WALLET =================

        user.wallet_balance = (
            current_balance - amount
        )

        # ================= SAFETY =================

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        # ================= TRANSACTION =================

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

        # ================= NOTIFICATION =================

        send_notification(
            user_id=user.id,
            title="Wallet Debited",
            message=f"₹{amount} deducted from wallet",
            type="payment",
            icon="money",
            action_url="/wallet",
            priority="normal"
        )

        # ================= COMMIT =================

        db.session.commit()

        return True

    except Exception as e:

        db.session.rollback()

        print("Deduct Money Error:", e)

        return False


# =====================================================
# TRANSFER MONEY
# =====================================================

def transfer_money(
    sender,
    receiver,
    amount
):

    try:

        # ================= VALIDATION =================

        if not sender or not receiver:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        # ================= SELF TRANSFER BLOCK =================

        if sender.id == receiver.id:
            return False

        sender_balance = float(
            sender.wallet_balance or 0
        )

        if sender_balance < amount:
            return False

        # ================= DEDUCT =================

        sender.wallet_balance = (
            sender_balance - amount
        )

        # ================= ADD =================

        receiver.wallet_balance = (
            float(receiver.wallet_balance or 0)
            + amount
        )

        # ================= SAFETY =================

        if sender.wallet_balance < 0:
            sender.wallet_balance = 0

        # ================= TRANSACTIONS =================

        sender_transaction = Transaction(

            transaction_id=generate_transaction_id(),

            user_id=sender.id,

            amount=amount,

            type="transfer_out",

            status="success",

            reason=f"Transfer to {receiver.name}"
        )

        receiver_transaction = Transaction(

            transaction_id=generate_transaction_id(),

            user_id=receiver.id,

            amount=amount,

            type="transfer_in",

            status="success",

            reason=f"Received from {sender.name}"
        )

        db.session.add(sender_transaction)
        db.session.add(receiver_transaction)

        db.session.flush()

        # ================= NOTIFICATIONS =================

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

        # ================= COMMIT =================

        db.session.commit()

        return True

    except Exception as e:

        db.session.rollback()

        print("Transfer Money Error:", e)

        return False


# =====================================================
# WITHDRAW MONEY
# =====================================================

def withdraw_money(
    user,
    amount
):

    try:

        # ================= VALIDATION =================

        if not user:
            return False

        amount = float(amount)

        if amount <= 0:
            return False

        balance = float(
            user.wallet_balance or 0
        )

        if balance < amount:
            return False

        # ================= UPDATE WALLET =================

        user.wallet_balance = (
            balance - amount
        )

        # ================= SAFETY =================

        if user.wallet_balance < 0:
            user.wallet_balance = 0

        # ================= TRANSACTION =================

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

        # ================= NOTIFICATION =================

        send_notification(
            user_id=user.id,
            title="Withdraw Requested",
            message=f"₹{amount} withdraw request submitted",
            type="payment",
            icon="money",
            action_url="/wallet",
            priority="high"
        )

        # ================= COMMIT =================

        db.session.commit()

        return True

    except Exception as e:

        db.session.rollback()

        print("Withdraw Error:", e)

        return False
