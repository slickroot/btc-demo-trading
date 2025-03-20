import datetime
import json
import os

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware


from pydantic import BaseModel
from typing import List

import httpx
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from motor.motor_asyncio import AsyncIOMotorClient

# Import configuration and models
import config
from models import Base, TradeOrder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Redis client using our config
redis_client = redis.from_url(config.REDIS_URL)

# Setup SQLAlchemy engine and session
engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Setup MongoDB client for trade logs
mongo_client = AsyncIOMotorClient(config.MONGO_URL)
mongo_db = mongo_client.trading
trade_logs_collection = mongo_db.trade_logs

# Pydantic models for request bodies and responses
class TradeRequest(BaseModel):
    type: str  # "buy" or "sell"
    amount: float

class CloseRequest(BaseModel):
    order_id: int

class TradeOrderResponse(BaseModel):
    id: int
    type: str
    amount: float
    price: float
    status: str
    created_at: datetime.datetime
    closed_at: datetime.datetime = None

@app.on_event("startup")
async def startup():
    # Create PostgreSQL tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def fetch_live_price() -> float:
    """
    Fetches the live Bitcoin price without caching.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://data-api.coindesk.com/index/cc/v1/latest/tick?market=cadli&instruments=BTC-USD", timeout=10.0)
            data = response.json()
            price = float(data["Data"]["BTC-USD"]["VALUE"])
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error fetching live price")
    return price

@app.get("/price")
async def get_price():
    price = await fetch_live_price()
    return {"price": price}

async def invalidate_order_cache():
    await redis_client.delete("order_history")

@app.get("/orders", response_model=List[TradeOrderResponse])
async def get_order_history():
    """
    Returns the list of all trade orders.
    Checks Redis for cached data, if not found queries PostgreSQL and caches the result.
    """
    cached = await redis_client.get("order_history")
    if cached:
        orders = json.loads(cached)
        return orders

    async with async_session() as session:
        result = await session.execute(select(TradeOrder))
        orders_objs = result.scalars().all()
        orders = [
            {
                "id": order.id,
                "type": order.type,
                "amount": order.amount,
                "price": order.price,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            }
            for order in orders_objs
        ]
    # Cache the order history as JSON for 30 seconds
    await redis_client.set("order_history", json.dumps(orders), ex=30)
    return orders

@app.post("/trade")
async def create_trade(trade: TradeRequest, background_tasks: BackgroundTasks):
    """
    Creates a new trade order at the current live price.
    Saves the order in PostgreSQL, logs the action in MongoDB, and invalidates the cached order history.
    """
    price = await fetch_live_price()

    async with async_session() as session:
        new_order = TradeOrder(type=trade.type, amount=trade.amount, price=price)
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)

    log_entry = {
        "order_id": new_order.id,
        "action": "create",
        "type": trade.type,
        "amount": trade.amount,
        "price": price,
        "status": "open",
        "timestamp": datetime.datetime.utcnow()
    }
    background_tasks.add_task(trade_logs_collection.insert_one, log_entry)
    background_tasks.add_task(invalidate_order_cache)

    return {"order_id": new_order.id, "price": price}

@app.post("/close")
async def close_trade(close_req: CloseRequest, background_tasks: BackgroundTasks):
    """
    Closes an open trade order.
    Updates its status in PostgreSQL, logs the closure in MongoDB, and invalidates the cached order history.
    """
    async with async_session() as session:
        result = await session.execute(
            select(TradeOrder).where(TradeOrder.id == close_req.order_id, TradeOrder.status == "open")
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Open order not found")

        order.status = "closed"
        order.closed_at = datetime.datetime.utcnow()
        await session.commit()
        await session.refresh(order)

    log_entry = {
        "order_id": order.id,
        "action": "close",
        "timestamp": datetime.datetime.utcnow()
    }
    background_tasks.add_task(trade_logs_collection.insert_one, log_entry)
    background_tasks.add_task(invalidate_order_cache)

    return {"order_id": order.id, "status": order.status}
