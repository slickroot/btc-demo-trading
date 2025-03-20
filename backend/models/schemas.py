import datetime
from typing import Optional, List
from pydantic import BaseModel

# Request schemas
class TradeRequest(BaseModel):
    type: str  # "buy" or "sell"
    amount: float

class CloseRequest(BaseModel):
    order_id: int

# Response schemas
class TradeOrderResponse(BaseModel):
    id: int
    type: str
    amount: float
    price: float
    status: str
    created_at: datetime.datetime
    closed_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

class AccountResponse(BaseModel):
    cash_balance: float
    btc_balance: float

    class Config:
        orm_mode = True

class PriceResponse(BaseModel):
    price: float

class TradeResponse(BaseModel):
    order_id: int
    price: float
    timestamp: datetime.datetime
    account: AccountResponse

class CloseResponse(BaseModel):
    order_id: int
    status: str
    timestamp: datetime.datetime
    account: AccountResponse
    close_price: float
