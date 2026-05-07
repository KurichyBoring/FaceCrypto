# FaceCrypto - Student Crypto Wallet Simulator

A full-featured cryptocurrency wallet simulation project for educational purposes. Built with Python FastAPI backend and TypeScript React frontend.

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Web framework
- **SQLAlchemy 2.0** (async) - ORM with SQLite/PostgreSQL support
- **Pydantic v2** - Data validation and settings
- **Alembic** - Database migrations
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **WebSocket** - Real-time chat support

### Frontend
- **TypeScript**
- **React 18**
- **Vite** - Build tool
- **React Router v6** - Routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **reconnecting-websocket** - WebSocket with auto-reconnect

## Project Structure

```
FaceCrypto/
├── backend/
│   ├── app/
│   │   ├── models.py          # SQLAlchemy models (User, Transaction, ChatMessage)
│   │   ├── schemas.py         # Pydantic schemas for validation
│   │   ├── database.py        # Database configuration
│   │   ├── config.py         # Settings management
│   │   ├── security.py       # JWT and password utilities
│   │   ├── dependencies.py   # Auth dependencies
│   │   ├── routers/          # API route handlers
│   │   │   ├── auth.py       # Registration, login, user info
│   │   │   ├── wallet.py     # Transfer, withdraw, history, exchange rates
│   │   │   ├── chat.py       # WebSocket chat + REST history
│   │   │   └── admin.py      # Admin panel endpoints
│   │   └── services/         # Business logic layer
│   │       ├── user_service.py
│   │       ├── wallet_service.py
│   │       └── chat_service.py
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/       # Reusable UI components
    │   ├── pages/            # Page components (Login, Wallet, Chat, Admin)
    │   ├── hooks/            # Custom hooks (useAuth, useWebSocket)
    │   ├── store/            # Zustand stores
    │   ├── types/            # TypeScript type definitions
    │   ├── api/              # API client layer
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── index.html
```

## Features

### Authentication & Authorization
- User registration with role selection (User/Admin)
- JWT-based authentication
- Protected routes with role-based access control
- Persistent login with localStorage

### Wallet Simulation
- Starting balance: $10,000 (simulated)
- **Transfer funds** to other users by username
- **Withdraw funds** to external addresses (simulated)
- **Simulated fees**: 1% for transfers, 2% for withdrawals
- **Transaction history** with timestamps and hashes
- **Simulated exchange rates** with random fluctuations
- Artificial delay (1.5-4s) for realistic processing simulation
- Auto-generated transaction hashes (like real blockchain)

### Real-time Chat
- WebSocket-based messaging
- User search by username
- Chat history persistence in database
- Unread message indicators
- Auto-reconnect on connection loss
- Message timestamps

### Admin Panel
- View all registered users
- System statistics (total users, transactions, volume)
- View all transactions across the system
- Extensible for future lab assignments

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd /home/kurichy/FaceCrypto/backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings if needed
```

5. Run the backend:
```bash
python run.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd /home/kurichy/FaceCrypto/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Wallet
- `GET /api/wallet/balance` - Get balance and wallet address
- `POST /api/wallet/transfer` - Transfer funds to user
- `POST /api/wallet/withdraw` - Withdraw funds (simulated)
- `GET /api/wallet/transactions` - Get transaction history
- `GET /api/wallet/exchange-rates` - Get simulated exchange rates

### Chat
- `WS /api/chat/ws?token=...` - WebSocket connection for real-time chat
- `GET /api/chat/history/{username}` - Get chat history with user
- `GET /api/chat/unread-count` - Get unread messages count
- `GET /api/chat/search-users?q=...` - Search users for chat

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/stats` - Get system statistics
- `GET /api/admin/transactions` - List all transactions

## Lab Assignment Extension Points

The following locations are marked for easy extension in future lab assignments:

- **Backend services** (`backend/app/services/`): Add new business logic here
- **New routers**: Add new API endpoints in `backend/app/routers/`
- **Admin panel**: Extend `frontend/src/pages/AdminPage.tsx` with new tabs
- **Wallet features**: Add new transaction types in `backend/app/models.py`
- **Chat features**: Extend `frontend/src/pages/ChatPage.tsx` with group chats, file sharing, etc.

## Design Notes

- **Flat design**: No gradients, clean borders, system typography
- **Colors**: Minimal palette with blue accent (#2563eb)
- **Icons**: SVG-based (can be added via `/frontend/src/assets/icons/`)
- **Responsive**: Designed for desktop lab environment

## Database

SQLite is used by default for simplicity. To switch to PostgreSQL:
1. Update `DATABASE_URL` in `.env`
2. Install `asyncpg` (already in requirements.txt)
3. Run migrations if needed with Alembic

## Testing

### Backend Testing

Install test dependencies:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Run all backend tests:
```bash
cd backend
source venv/bin/activate
pytest
```

Run with coverage:
```bash
cd backend
source venv/bin/activate
pytest --cov=app --cov-report=term-missing
```

### Frontend Testing

Install test dependencies:
```bash
cd frontend
npm install
```

Run unit tests:
```bash
cd frontend
npm run test
```

Run E2E tests (requires both backend and frontend running):
```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

Run E2E tests with UI:
```bash
cd frontend
npm run test:e2e:ui
```

### Test Structure

- `backend/tests/test_services.py` - Service layer unit tests
- `backend/tests/test_api.py` - API integration tests
- `frontend/src/**/*.test.tsx` - Frontend component tests
- `frontend/src/**/*.test.ts` - Frontend logic tests
- `frontend/e2e/*.spec.ts` - E2E tests

## License

Educational use only. Not for production use.
# test
