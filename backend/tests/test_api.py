import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# ========== AUTH ENDPOINTS ==========

@pytest.mark.asyncio
async def test_register_user_success(client):
    response = await client.post("/api/auth/register", json={
        "username": "newuser1",
        "email": "new1@example.com",
        "password": "password123",
        "role": "user"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser1"
    assert data["email"] == "new1@example.com"
    assert "wallet_address" in data
    assert data["balance"] == 10000.0


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/api/auth/register", json={
        "username": "duplicate",
        "email": "dup1@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/register", json={
        "username": "duplicate",
        "email": "dup2@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "same@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/register", json={
        "username": "user2",
        "email": "same@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await client.post("/api/auth/register", json={
        "username": "invalidemail",
        "email": "not-an-email",
        "password": "password123"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    response = await client.post("/api/auth/register", json={
        "username": "shortpass",
        "email": "short@example.com",
        "password": "123"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={
        "username": "logintest",
        "email": "login@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/login", json={
        "username": "logintest",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={
        "username": "logintest2",
        "email": "login2@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/login", json={
        "username": "logintest2",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "password123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(client, auth_token):
    response = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "email" in data


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me_invalid_token(client):
    response = await client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401


# ========== WALLET ENDPOINTS ==========

@pytest.mark.asyncio
async def test_get_balance_success(client, auth_token):
    response = await client.get("/api/wallet/balance", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "wallet_address" in data
    assert data["balance"] == 10000.0


@pytest.mark.asyncio
async def test_get_balance_no_auth(client):
    response = await client.get("/api/wallet/balance")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_transfer_success(client, auth_token, db_session):
    # Create receiver first
    from app.services.user_service import create_user
    from app.schemas import UserCreate

    receiver = await create_user(db_session, UserCreate(
        username="receiver1",
        email="receiver1@example.com",
        password="password123"
    ))

    response = await client.post("/api/wallet/transfer",
        json={"receiver_username": "receiver1", "amount": 100.0},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.0
    assert data["tx_type"] == "transfer"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_transfer_insufficient_funds(client, auth_token, db_session):
    from app.services.user_service import create_user
    from app.schemas import UserCreate

    receiver = await create_user(db_session, UserCreate(
        username="receiver2",
        email="receiver2@example.com",
        password="password123"
    ))

    response = await client.post("/api/wallet/transfer",
        json={"receiver_username": "receiver2", "amount": 999999.0},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transfer_receiver_not_found(client, auth_token):
    response = await client.post("/api/wallet/transfer",
        json={"receiver_username": "nonexistent", "amount": 100.0},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "Receiver not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transfer_to_self(client, auth_token):
    response = await client.post("/api/wallet/transfer",
        json={"receiver_username": "testuser", "amount": 100.0},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert "Cannot transfer to yourself" in response.json()["detail"]


@pytest.mark.asyncio
async def test_withdraw_success(client, auth_token):
    response = await client.post("/api/wallet/withdraw",
        json={"amount": 100.0, "address": "0xexternaladdress1234567890"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.0
    assert data["tx_type"] == "withdrawal"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_withdraw_invalid_address(client, auth_token):
    response = await client.post("/api/wallet/withdraw",
        json={"amount": 100.0, "address": "short"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_exchange_rates(client):
    response = await client.get("/api/wallet/exchange-rates")
    assert response.status_code == 200
    data = response.json()
    assert "btc_usd" in data
    assert "eth_usd" in data


# ========== ADMIN ENDPOINTS ==========

@pytest.mark.asyncio
async def test_admin_get_users_success(client, admin_token):
    response = await client.get("/api/admin/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_get_users_forbidden(client, auth_token):
    response = await client.get("/api/admin/users", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_get_stats(client, admin_token):
    response = await client.get("/api/admin/stats", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_transactions" in data
    assert "total_volume" in data


@pytest.mark.asyncio
async def test_admin_get_transactions(client, admin_token):
    response = await client.get("/api/admin/transactions", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)
