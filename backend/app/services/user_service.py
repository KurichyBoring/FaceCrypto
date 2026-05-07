from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserRole
from app.schemas import UserCreate
from app.security import get_password_hash, verify_password


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    from app.services.wallet_service import generate_wallet_address

    existing = await db.execute(
        select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    )
    if existing.scalar_one_or_none():
        raise ValueError("Username or email already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        wallet_address=generate_wallet_address(user_data.username),
        balance=10000.0
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def search_users(db: AsyncSession, query: str) -> list[User]:
    from sqlalchemy import or_
    result = await db.execute(
        select(User).where(
            or_(User.username.ilike(f"%{query}%"), User.id == query if query.isdigit() else False)
        ).limit(20)
    )
    return result.scalars().all()
