from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.models import UserRole, TransactionType, TransactionStatus


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    wallet_address: str
    balance: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WalletTransfer(BaseModel):
    receiver_username: str
    amount: float = Field(..., gt=0)


class WalletWithdraw(BaseModel):
    amount: float = Field(..., gt=0)
    address: str = Field(..., min_length=10)


class TransactionResponse(BaseModel):
    id: int
    hash: str
    sender_id: Optional[int]
    receiver_id: Optional[int]
    amount: float
    fee: float
    tx_type: TransactionType
    status: TransactionStatus
    created_at: datetime
    sender_username: Optional[str] = None
    receiver_username: Optional[str] = None

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    receiver_username: str
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    sender_username: str
    receiver_username: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ExchangeRateResponse(BaseModel):
    btc_usd: float
    eth_usd: float
    updated_at: datetime


class UserSearchResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True
