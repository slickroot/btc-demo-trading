import datetime
from typing import List, Dict, Any
from fastapi import HTTPException, BackgroundTasks
from pymongo import MongoClient
from config import MONGODB_URL, MONGODB_DB
from repositories.orders_repo import OrderRepository
from services.account_service import AccountService
from services.price_service import PriceService
from services.cache_service import CacheService

class OrderService:
    def __init__(
        self, 
        order_repo: OrderRepository, 
        account_service: AccountService,
        cache_service: CacheService,
        background_tasks: BackgroundTasks = None
    ):
        self.order_repo = order_repo
        self.account_service = account_service
        self.cache_service = cache_service
        self.background_tasks = background_tasks
        
        # MongoDB setup
        self.mongo_client = MongoClient(MONGODB_URL)
        self.db = self.mongo_client[MONGODB_DB]
        self.trade_logs_collection = self.db["trade_logs"]
    
    async def get_order_history(self) -> List[Dict[str, Any]]:
        """
        Get the order history, using cache if available
        """
        cached = await self.cache_service.get_json("order_history")
        if cached:
            return cached
            
        orders = await self.order_repo.get_all_orders()
        orders_json = [
            {
                "id": order.id,
                "type": order.type,
                "amount": order.amount,
                "price": order.price,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            }
            for order in orders
        ]
        
        # Cache the order history for 30 seconds
        await self.cache_service.set_json("order_history", orders_json, 30)
        return orders_json
    
    async def invalidate_order_cache(self):
        """
        Invalidate the order history cache
        """
        await self.cache_service.delete("order_history")
    
    async def log_trade_action(self, log_entry: Dict[str, Any]):
        """
        Log a trade action to MongoDB
        """
        self.trade_logs_collection.insert_one(log_entry)
    
    async def create_trade(self, trade_type: str, amount: float) -> Dict[str, Any]:
        """
        Create a new trade order
        """
        price = await PriceService.fetch_live_price()
        
        if trade_type.lower() not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Invalid trade type")
        
        # Update account based on trade type
        if trade_type.lower() == "buy":
            account = await self.account_service.process_buy(amount, price)
        else:  # sell
            account = await self.account_service.process_sell(amount, price)
            
        # Create the order
        new_order = await self.order_repo.create_order(trade_type, amount, price)
        
        # Log the action
        log_entry = {
            "order_id": new_order.id,
            "action": "create",
            "type": trade_type,
            "amount": amount,
            "price": price,
            "status": "open",
            "timestamp": datetime.datetime.utcnow()
        }
        
        if self.background_tasks:
            self.background_tasks.add_task(self.log_trade_action, log_entry)
            self.background_tasks.add_task(self.invalidate_order_cache)
        
        return {
            "order_id": new_order.id,
            "price": price,
            "timestamp": new_order.created_at,
            "account": {"cash_balance": account.cash_balance, "btc_balance": account.btc_balance}
        }
    
    async def close_trade(self, order_id: int) -> Dict[str, Any]:
        """
        Close an existing trade order
        """
        current_price = await PriceService.fetch_live_price()
        
        # Get the order
        order = await self.order_repo.get_open_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Open order not found")
        
        # Update account based on order type
        if order.type.lower() == "buy":
            account = await self.account_service.close_buy_order(order.amount, current_price)
        else:  # sell
            account = await self.account_service.close_sell_order(order.amount, current_price)
        
        # Close the order
        order = await self.order_repo.close_order(order_id)
        
        # Log the action
        log_entry = {
            "order_id": order.id,
            "action": "close",
            "timestamp": datetime.datetime.utcnow(),
            "close_price": current_price,
        }
        
        if self.background_tasks:
            self.background_tasks.add_task(self.log_trade_action, log_entry)
            self.background_tasks.add_task(self.invalidate_order_cache)
        
        return {
            "order_id": order.id,
            "status": order.status,
            "timestamp": order.closed_at,
            "account": {"cash_balance": account.cash_balance, "btc_balance": account.btc_balance},
            "close_price": current_price,
        }
