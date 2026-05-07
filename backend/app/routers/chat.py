from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, async_session
from app.dependencies import get_current_user
from app.models import User, ChatMessage
from app.schemas import ChatMessageCreate, ChatMessageResponse, UserSearchResponse
from app.services.chat_service import save_message, get_chat_history, mark_messages_read, get_unread_count

router = APIRouter(prefix="/chat", tags=["chat"])

active_connections: dict[int, WebSocket] = {}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    from jose import JWTError, jwt
    from app.config import settings
    from app.models import User

    if not token:
        await websocket.close(code=4000)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        await websocket.close(code=4000)
        return

    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            receiver_username = data.get("receiver")
            content = data.get("content")

            if not receiver_username or not content:
                continue

            async with async_session() as db:
                receiver_result = await db.execute(select(User).where(User.username == receiver_username))
                receiver = receiver_result.scalar_one_or_none()
                if not receiver:
                    await websocket.send_json({"error": "Receiver not found"})
                    continue

                msg = await save_message(db, user_id, receiver.id, content)
                msg_response = ChatMessageResponse(
                    id=msg.id,
                    sender_id=msg.sender_id,
                    receiver_id=msg.receiver_id,
                    sender_username=msg.sender.username,
                    receiver_username=receiver.username,
                    content=msg.content,
                    is_read=msg.is_read,
                    created_at=msg.created_at
                )

                await websocket.send_json(msg_response.model_dump(mode="json"))

                if receiver.id in active_connections:
                    await active_connections[receiver.id].send_json(msg_response.model_dump(mode="json"))

    except WebSocketDisconnect:
        active_connections.pop(user_id, None)
    except Exception:
        active_connections.pop(user_id, None)


@router.get("/history/{other_username}", response_model=list[ChatMessageResponse])
async def get_history(
    other_username: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    other = await db.execute(select(User).where(User.username == other_username))
    other_user = other.scalar_one_or_none()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    messages = await get_chat_history(db, current_user.id, other_user.id, limit)
    await mark_messages_read(db, current_user.id, other_user.id)

    return [
        ChatMessageResponse(
            id=m.id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            sender_username=m.sender.username,
            receiver_username=m.receiver.username,
            content=m.content,
            is_read=m.is_read,
            created_at=m.created_at
        ) for m in messages
    ]


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count = await get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.get("/search-users", response_model=list[UserSearchResponse])
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.services.user_service import search_users as search_fn
    users = await search_fn(db, q)
    return [u for u in users if u.id != current_user.id]
