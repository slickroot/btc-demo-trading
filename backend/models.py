import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TradeOrder(Base):
    __tablename__ = "trade_orders"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # "buy" or "sell"
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="open")  # "open" or "closed"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
