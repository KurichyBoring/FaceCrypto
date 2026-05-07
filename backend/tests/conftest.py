import pytest
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import User, UserRole, Transaction, ChatMessage

# Test database URL - use env or default
import os
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test_facecrypto.db")

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


# Override get_db dependency
async def override_get_db():
    async with test_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with test_async_session() as session:
        yield session
        # Cleanup
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db_session):
    from app.services.user_service import create_user
    from app.schemas import UserCreate

    user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
    user = await create_user(db_session, user_data)
    return user


@pytest.fixture
async def admin_user(db_session):
    from app.services.user_service import create_user
    from app.schemas import UserCreate

    user_data = UserCreate(username="admin", email="admin@example.com", password="admin123", role="admin")
    user = await create_user(db_session, user_data)
    return user


@pytest.fixture
async def auth_token(client, test_user):
    response = await client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
async def admin_token(client, admin_user):
    response = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]
