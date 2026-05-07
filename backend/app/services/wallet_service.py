import hashlib
import random
import asyncio
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Transaction, TransactionType, TransactionStatus
from app.schemas import TransactionResponse
from app.security import get_password_hash


def generate_wallet_address(username: str) -> str:
    import time
    raw = f"{username}{time.time()}{random.random()}"
    return "0x" + hashlib.sha256(raw.encode()).hexdigest()[:40]


def generate_tx_hash() -> str:
    import time
    raw = f"{time.time()}{random.random()}{random.random()}"
    return "0x" + hashlib.sha256(raw.encode()).hexdigest()


def get_simulated_exchange_rate() -> dict:
    base_btc = 45000.0
    base_eth = 3000.0
    fluctuation = 0.05
    btc_rate = base_btc + random.uniform(-base_btc * fluctuation, base_btc * fluctuation)
    eth_rate = base_eth + random.uniform(-base_eth * fluctuation, base_eth * fluctuation)
    return {
        "btc_usd": round(btc_rate, 2),
        "eth_usd": round(eth_rate, 2),
        "updated_at": datetime.utcnow()
    }


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def transfer_funds(db: AsyncSession, sender: User, receiver_username: str, amount: float) -> Transaction:
    if amount <= 0:
        raise ValueError("Amount must be positive")

    fee_percent = 0.01
    fee = Decimal(str(amount)) * Decimal(str(fee_percent))
    total = Decimal(str(amount)) + fee

    if Decimal(str(sender.balance)) < total:
        raise ValueError("Insufficient funds")

    receiver = await get_user_by_username(db, receiver_username)
    if not receiver:
        raise ValueError("Receiver not found")

    if sender.id == receiver.id:
        raise ValueError("Cannot transfer to yourself")

    tx_hash = generate_tx_hash()
    tx = Transaction(
        hash=tx_hash,
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=Decimal(str(amount)),
        fee=fee,
        tx_type=TransactionType.TRANSFER,
        status=TransactionStatus.PENDING
    )
    db.add(tx)
    await db.flush()

    await asyncio.sleep(random.uniform(1.5, 3.0))

    sender.balance = Decimal(str(sender.balance)) - total
    receiver.balance = Decimal(str(receiver.balance)) + Decimal(str(amount))
    tx.status = TransactionStatus.COMPLETED

    await db.commit()
    await db.refresh(tx)
    return tx


async def withdraw_funds(db: AsyncSession, user: User, amount: float, address: str) -> Transaction:
    if amount <= 0:
        raise ValueError("Amount must be positive")

    fee_percent = 0.02
    fee = Decimal(str(amount)) * Decimal(str(fee_percent))
    total = Decimal(str(amount)) + fee

    if Decimal(str(user.balance)) < total:
        raise ValueError("Insufficient funds")

    tx_hash = generate_tx_hash()
    tx = Transaction(
        hash=tx_hash,
        sender_id=user.id,
        receiver_id=None,
        amount=Decimal(str(amount)),
        fee=fee,
        tx_type=TransactionType.WITHDRAWAL,
        status=TransactionStatus.PENDING
    )
    db.add(tx)
    await db.flush()

    await asyncio.sleep(random.uniform(2.0, 4.0))

    user.balance = Decimal(str(user.balance)) - total
    tx.status = TransactionStatus.COMPLETED

    await db.commit()
    await db.refresh(tx)
    return tx


async def get_transaction_history(db: AsyncSession, user_id: int, limit: int = 50) -> list[Transaction]:
    result = await db.execute(
        select(Transaction)
        .where((Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id))
        .order_by(desc(Transaction.created_at))
        .limit(limit)
    )
    return result.scalars().all()
