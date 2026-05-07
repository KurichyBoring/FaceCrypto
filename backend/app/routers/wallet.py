from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Transaction, TransactionType, TransactionStatus
from app.schemas import WalletTransfer, WalletWithdraw, TransactionResponse, ExchangeRateResponse
from app.services.wallet_service import (
    transfer_funds, withdraw_funds, get_transaction_history,
    get_simulated_exchange_rate
)

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/balance")
async def get_balance(current_user: User = Depends(get_current_user)):
    return {
        "balance": float(current_user.balance),
        "wallet_address": current_user.wallet_address,
        "username": current_user.username
    }


@router.post("/transfer", response_model=TransactionResponse)
async def transfer(
    data: WalletTransfer,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        tx = await transfer_funds(db, current_user, data.receiver_username, data.amount)
        return TransactionResponse(
            id=tx.id,
            hash=tx.hash,
            sender_id=tx.sender_id,
            receiver_id=tx.receiver_id,
            amount=float(tx.amount),
            fee=float(tx.fee),
            tx_type=tx.tx_type,
            status=tx.status,
            created_at=tx.created_at,
            sender_username=current_user.username,
            receiver_username=data.receiver_username
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw", response_model=TransactionResponse)
async def withdraw(
    data: WalletWithdraw,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        tx = await withdraw_funds(db, current_user, data.amount, data.address)
        return TransactionResponse(
            id=tx.id,
            hash=tx.hash,
            sender_id=tx.sender_id,
            receiver_id=tx.receiver_id,
            amount=float(tx.amount),
            fee=float(tx.fee),
            tx_type=tx.tx_type,
            status=tx.status,
            created_at=tx.created_at,
            sender_username=current_user.username
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    txs = await get_transaction_history(db, current_user.id, limit)
    result = []
    for tx in txs:
        sender_username = None
        receiver_username = None
        if tx.sender:
            sender_username = tx.sender.username
        if tx.receiver:
            receiver_username = tx.receiver.username
        result.append(TransactionResponse(
            id=tx.id,
            hash=tx.hash,
            sender_id=tx.sender_id,
            receiver_id=tx.receiver_id,
            amount=float(tx.amount),
            fee=float(tx.fee),
            tx_type=tx.tx_type,
            status=tx.status,
            created_at=tx.created_at,
            sender_username=sender_username,
            receiver_username=receiver_username
        ))
    return result


@router.get("/exchange-rates", response_model=ExchangeRateResponse)
async def get_rates():
    return get_simulated_exchange_rate()
