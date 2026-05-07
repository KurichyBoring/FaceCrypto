import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import create_user, authenticate_user, get_all_users, search_users
from app.services.wallet_service import transfer_funds, withdraw_funds, get_transaction_history, get_simulated_exchange_rate, generate_wallet_address, generate_tx_hash
from app.schemas import UserCreate
from app.models import User, Transaction, TransactionType, TransactionStatus


# ========== USER SERVICE TESTS ==========

@pytest.mark.asyncio
async def test_create_user_success(db_session):
    user_data = UserCreate(username="newuser", email="new@example.com", password="password123")
    user = await create_user(db_session, user_data)
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.balance == 10000.0
    assert user.wallet_address.startswith("0x")


@pytest.mark.asyncio
async def test_create_user_duplicate_username(db_session):
    from app.models import User
    from app.security import get_password_hash

    user = User(
        username="existing",
        email="existing@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x123"
    )
    db_session.add(user)
    await db_session.commit()

    from app.services.user_service import create_user
    from app.schemas import UserCreate

    user_data = UserCreate(username="existing", email="new@example.com", password="password123")
    with pytest.raises(ValueError, match="Username or email already exists"):
        await create_user(db_session, user_data)


@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_session):
    from app.models import User
    from app.security import get_password_hash

    user = User(
        username="existing",
        email="existing@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x123"
    )
    db_session.add(user)
    await db_session.commit()

    from app.schemas import UserCreate

    user_data = UserCreate(username="newuser", email="existing@example.com", password="password123")
    with pytest.raises(ValueError, match="Username or email already exists"):
        await create_user(db_session, user_data)


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session):
    from app.security import get_password_hash
    from app.models import User

    user = User(
        username="authuser",
        email="auth@example.com",
        hashed_password=get_password_hash("password123"),
        wallet_address="0x456"
    )
    db_session.add(user)
    await db_session.commit()

    authenticated = await authenticate_user(db_session, "authuser", "password123")
    assert authenticated is not None
    assert authenticated.username == "authuser"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session):
    from app.security import get_password_hash
    from app.models import User

    user = User(
        username="authuser2",
        email="auth2@example.com",
        hashed_password=get_password_hash("password123"),
        wallet_address="0x789"
    )
    db_session.add(user)
    await db_session.commit()

    authenticated = await authenticate_user(db_session, "authuser2", "wrongpassword")
    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found(db_session):
    authenticated = await authenticate_user(db_session, "nonexistent", "password123")
    assert authenticated is None


# ========== WALLET SERVICE TESTS ==========

@pytest.mark.asyncio
async def test_generate_wallet_address():
    addr1 = generate_wallet_address("user1")
    addr2 = generate_wallet_address("user2")
    assert addr1.startswith("0x")
    assert addr2.startswith("0x")
    assert addr1 != addr2
    assert len(addr1) == 42  # 0x + 40 hex chars


@pytest.mark.asyncio
async def test_generate_tx_hash():
    hash1 = generate_tx_hash()
    hash2 = generate_tx_hash()
    assert hash1.startswith("0x")
    assert hash2.startswith("0x")
    assert hash1 != hash2


@pytest.mark.asyncio
async def test_get_simulated_exchange_rate():
    rate = get_simulated_exchange_rate()
    assert "btc_usd" in rate
    assert "eth_usd" in rate
    assert "updated_at" in rate
    assert 40000 < rate["btc_usd"] < 50000
    assert 2500 < rate["eth_usd"] < 3500


@pytest.mark.asyncio
async def test_transfer_funds_success(db_session):
    from app.security import get_password_hash
    from app.models import User

    sender = User(
        username="sender",
        email="sender@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x111",
        balance=10000.0
    )
    receiver = User(
        username="receiver",
        email="receiver@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x222",
        balance=5000.0
    )
    db_session.add_all([sender, receiver])
    await db_session.commit()

    tx = await transfer_funds(db_session, sender, "receiver", 100.0)
    assert tx.amount == 100.0
    assert tx.fee == 1.0  # 1% fee
    assert tx.tx_type == TransactionType.TRANSFER
    assert tx.status == TransactionStatus.COMPLETED

    await db_session.refresh(sender)
    await db_session.refresh(receiver)
    assert float(sender.balance) == 10000.0 - 101.0  # 100 + 1 fee
    assert float(receiver.balance) == 5000.0 + 100.0


@pytest.mark.asyncio
async def test_transfer_insufficient_funds(db_session):
    from app.security import get_password_hash
    from app.models import User

    sender = User(
        username="broke",
        email="broke@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x333",
        balance=50.0
    )
    receiver = User(
        username="rich",
        email="rich@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x444",
        balance=5000.0
    )
    db_session.add_all([sender, receiver])
    await db_session.commit()

    with pytest.raises(ValueError, match="Insufficient funds"):
        await transfer_funds(db_session, sender, "rich", 1000.0)


@pytest.mark.asyncio
async def test_transfer_receiver_not_found(db_session):
    from app.security import get_password_hash
    from app.models import User

    sender = User(
        username="sender2",
        email="sender2@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x555",
        balance=10000.0
    )
    db_session.add(sender)
    await db_session.commit()

    with pytest.raises(ValueError, match="Receiver not found"):
        await transfer_funds(db_session, sender, "nonexistent", 100.0)


@pytest.mark.asyncio
async def test_transfer_to_self(db_session):
    from app.security import get_password_hash
    from app.models import User

    user = User(
        username="selfie",
        email="selfie@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x666",
        balance=10000.0
    )
    db_session.add(user)
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot transfer to yourself"):
        await transfer_funds(db_session, user, "selfie", 100.0)


@pytest.mark.asyncio
async def test_withdraw_funds_success(db_session):
    from app.security import get_password_hash
    from app.models import User

    user = User(
        username="withdrawer",
        email="withdraw@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x777",
        balance=10000.0
    )
    db_session.add(user)
    await db_session.commit()

    tx = await withdraw_funds(db_session, user, 100.0, "0xexternal123")
    assert tx.amount == 100.0
    assert tx.fee == 2.0  # 2% fee
    assert tx.tx_type == TransactionType.WITHDRAWAL
    assert tx.status == TransactionStatus.COMPLETED

    await db_session.refresh(user)
    assert float(user.balance) == 10000.0 - 102.0  # 100 + 2 fee


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(db_session):
    from app.security import get_password_hash
    from app.models import User

    user = User(
        username="broke2",
        email="broke2@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x888",
        balance=50.0
    )
    db_session.add(user)
    await db_session.commit()

    with pytest.raises(ValueError, match="Insufficient funds"):
        await withdraw_funds(db_session, user, 1000.0, "0xexternal")


@pytest.mark.asyncio
async def test_get_transaction_history(db_session):
    from app.security import get_password_hash
    from app.models import User

    user = User(
        username="txuser",
        email="tx@example.com",
        hashed_password=get_password_hash("pass"),
        wallet_address="0x999",
        balance=10000.0
    )
    db_session.add(user)
    await db_session.commit()

    txs = await get_transaction_history(db_session, user.id, 50)
    assert isinstance(txs, list)
