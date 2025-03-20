from typing import List, Optional
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import TradeOrder

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_orders(self) -> List[TradeOrder]:
        """Get all trade orders"""
        result = await self.session.execute(select(TradeOrder))
        return result.scalars().all()

    async def get_order_by_id(self, order_id: int) -> Optional[TradeOrder]:
        """Get a specific order by ID"""
        result = await self.session.execute(
            select(TradeOrder).where(TradeOrder.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_open_order_by_id(self, order_id: int) -> Optional[TradeOrder]:
        """Get a specific open order by ID"""
        result = await self.session.execute(
            select(TradeOrder).where(TradeOrder.id == order_id, TradeOrder.status == "open")
        )
        return result.scalar_one_or_none()

    async def create_order(self, type: str, amount: float, price: float) -> TradeOrder:
        """Create a new trade order"""
        new_order = TradeOrder(type=type, amount=amount, price=price)
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)
        return new_order

    async def close_order(self, order_id: int) -> Optional[TradeOrder]:
        """Mark an order as closed"""
        order = await self.get_open_order_by_id(order_id)
        if not order:
            return None
        
        order.status = "closed"
        order.closed_at = datetime.datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(order)
        return order
