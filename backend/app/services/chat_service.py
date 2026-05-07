from sqlalchemy import select, desc, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ChatMessage, User
from app.schemas import ChatMessageResponse


async def save_message(db: AsyncSession, sender_id: int, receiver_id: int, content: str) -> ChatMessage:
    msg = ChatMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    
    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.sender), selectinload(ChatMessage.receiver))
        .where(ChatMessage.id == msg.id)
    )
    return result.scalar_one()


async def get_chat_history(db: AsyncSession, user_id: int, other_user_id: int, limit: int = 100) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.sender), selectinload(ChatMessage.receiver))
        .where(
            or_(
                and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == other_user_id),
                and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == user_id)
            )
        )
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    return list(reversed(result.scalars().all()))


async def mark_messages_read(db: AsyncSession, receiver_id: int, sender_id: int):
    from sqlalchemy import update
    await db.execute(
        update(ChatMessage)
        .where(
            and_(ChatMessage.receiver_id == receiver_id, ChatMessage.sender_id == sender_id, ChatMessage.is_read == False)
        )
        .values(is_read=True)
    )
    await db.commit()


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(ChatMessage.id))
        .where(and_(ChatMessage.receiver_id == user_id, ChatMessage.is_read == False))
    )
    return result.scalar_one()
