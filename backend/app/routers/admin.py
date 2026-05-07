from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.dependencies import get_current_admin
from app.models import User, Transaction, UserRole, TransactionType
from app.schemas import UserResponse, TransactionResponse
from app.services.user_service import get_all_users

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = await get_all_users(db, skip, limit)
    return users


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users_count = await db.execute(select(func.count(User.id)))
    tx_count = await db.execute(select(func.count(Transaction.id)))
    total_volume = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.status == 'completed'
        )
    )
    return {
        "total_users": users_count.scalar_one(),
        "total_transactions": tx_count.scalar_one(),
        "total_volume": float(total_volume.scalar_one())
    }


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_all_transactions(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    result = await db.execute(
        select(Transaction).order_by(desc(Transaction.created_at)).limit(limit)
    )
    txs = result.scalars().all()
    response = []
    for tx in txs:
        sender_username = tx.sender.username if tx.sender else None
        receiver_username = tx.receiver.username if tx.receiver else None
        response.append(TransactionResponse(
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
    return response
