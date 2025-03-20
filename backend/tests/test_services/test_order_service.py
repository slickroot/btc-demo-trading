import pytest
import unittest
import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, BackgroundTasks
from services.order_service import OrderService
from models.db_models import Account, TradeOrder

class TestOrderService:
    
    def setup_method(self, method):
        self.mock_order_repo = AsyncMock()
        self.mock_account_service = AsyncMock()
        self.mock_cache_service = AsyncMock()
        self.mock_bg_tasks = MagicMock(spec=BackgroundTasks)
        
        # Mock MongoDB
        self.mock_collection = MagicMock()
        self.patch_mongo = patch('pymongo.MongoClient', autospec=True)
        self.mock_mongo_client = self.patch_mongo.start()
        self.mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value = self.mock_collection
        
        self.service = OrderService(
            self.mock_order_repo,
            self.mock_account_service,
            self.mock_cache_service,
            self.mock_bg_tasks
        )
    
    def teardown_method(self):
        self.patch_mongo.stop()
    
    @pytest.mark.asyncio
    async def test_get_order_history_from_cache(self):
        """Test getting order history from cache"""
        cached_orders = [{"id": 1, "type": "buy", "amount": 0.1}]
        self.mock_cache_service.get_json.return_value = cached_orders
        
        result = await self.service.get_order_history()
        
        assert result == cached_orders
        self.mock_cache_service.get_json.assert_called_once_with("order_history")
        # Verify we didn't query the database
        self.mock_order_repo.get_all_orders.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_order_history_from_db(self):
        """Test getting order history from database when not in cache"""
        # Set up cache miss
        self.mock_cache_service.get_json.return_value = None
        
        # Set up mock orders
        created_at = datetime.datetime(2025, 3, 1, 12, 0, 0)
        mock_orders = [
            MagicMock(
                id=1, 
                type="buy", 
                amount=0.1, 
                price=50000.0, 
                status="open",
                created_at=created_at,
                closed_at=None
            )
        ]
        self.mock_order_repo.get_all_orders.return_value = mock_orders
        
        result = await self.service.get_order_history()
        
        # Verify we queried both cache and database
        self.mock_cache_service.get_json.assert_called_once_with("order_history")
        self.mock_order_repo.get_all_orders.assert_called_once()
        
        # Verify we cached the result
        self.mock_cache_service.set_json.assert_called_once()
        call_args = self.mock_cache_service.set_json.call_args
        assert call_args[0][0] == "order_history"
        assert isinstance(call_args[0][1], list)
        assert call_args[0][1][0]["id"] == 1
        assert call_args[0][2] == 30  # 30 second expiration
        
        # Verify the returned data
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["type"] == "buy"
    
    @pytest.mark.asyncio
    async def test_invalidate_order_cache(self):
        """Test invalidating the order cache"""
        await self.service.invalidate_order_cache()
        self.mock_cache_service.delete.assert_called_once_with("order_history")
    
    @pytest.mark.asyncio
    async def test_create_trade_buy(self):
        """Test creating a buy trade"""
        with patch('services.price_service.PriceService.fetch_live_price', return_value=50000.0):
            # Set up mock account after buy
            mock_account = MagicMock(cash_balance=5000.0, btc_balance=1.1)
            self.mock_account_service.process_buy.return_value = mock_account
            
            # Set up mock order
            mock_order = MagicMock(
                id=1, 
                type="buy", 
                amount=0.1, 
                price=50000.0,
                created_at=datetime.datetime(2025, 3, 1, 12, 0, 0)
            )
            self.mock_order_repo.create_order.return_value = mock_order
            
            # Execute the trade
            result = await self.service.create_trade("buy", 0.1)
            
            # Verify account service was called
            self.mock_account_service.process_buy.assert_called_once_with(0.1, 50000.0)
            
            # Verify order was created
            self.mock_order_repo.create_order.assert_called_once_with("buy", 0.1, 50000.0)
            
            # Verify background tasks were added
            assert self.mock_bg_tasks.add_task.call_count == 2
            
            # Verify the result
            assert result["order_id"] == 1
            assert result["price"] == 50000.0
            assert result["account"]["cash_balance"] == 5000.0
            assert result["account"]["btc_balance"] == 1.1

    @pytest.mark.asyncio
    async def test_create_trade_sell(self):
        """Test creating a sell trade"""
        with patch('services.price_service.PriceService.fetch_live_price', return_value=50000.0):
            mock_account = MagicMock(cash_balance=15000.0, btc_balance=0.3)
            self.mock_account_service.process_sell.return_value = mock_account

            mock_order = MagicMock(
                id=2,
                type="sell",
                amount=0.2,
                price=50000.0,
                created_at=datetime.datetime(2025, 3, 1, 13, 0, 0)
            )
            self.mock_order_repo.create_order.return_value = mock_order

            result = await self.service.create_trade("sell", 0.2)

            self.mock_account_service.process_sell.assert_called_once_with(0.2, 50000.0)
            self.mock_order_repo.create_order.assert_called_once_with("sell", 0.2, 50000.0)

            assert result["order_id"] == 2
            assert result["price"] == 50000.0
            assert result["account"]["cash_balance"] == 15000.0
            assert result["account"]["btc_balance"] == 0.3

    @pytest.mark.asyncio
    async def test_create_trade_invalid_type(self):
        """Test creating a trade with an invalid type"""
        with pytest.raises(HTTPException) as excinfo:
            await self.service.create_trade("hold", 0.1)
        assert excinfo.value.status_code == 400

    @pytest.mark.asyncio
    async def test_close_trade_buy(self):
        """Test closing a buy trade order"""
        with patch('services.price_service.PriceService.fetch_live_price', return_value=55000.0):
            # Set up an open buy order
            mock_order = MagicMock(
                id=3,
                type="buy",
                amount=0.1,
                price=50000.0,
                created_at=datetime.datetime(2025, 3, 1, 14, 0, 0),
                closed_at=None,
                status="open"
            )
            self.mock_order_repo.get_open_order_by_id.return_value = mock_order

            # Set up account service for closing buy order
            mock_account = MagicMock(cash_balance=6000.0, btc_balance=0.9)
            self.mock_account_service.close_buy_order.return_value = mock_account

            # Simulate that closing order in repo returns order with updated status and closed_at
            mock_closed_order = MagicMock(
                id=3,
                type="buy",
                amount=0.1,
                price=50000.0,
                created_at=mock_order.created_at,
                closed_at=datetime.datetime(2025, 3, 1, 14, 5, 0),
                status="closed"
            )
            self.mock_order_repo.close_order.return_value = mock_closed_order

            result = await self.service.close_trade(3)

            self.mock_order_repo.get_open_order_by_id.assert_called_once_with(3)
            self.mock_account_service.close_buy_order.assert_called_once_with(0.1, 55000.0)
            self.mock_order_repo.close_order.assert_called_once_with(3)

            assert result["order_id"] == 3
            assert result["status"] == "closed"
            assert result["account"]["cash_balance"] == 6000.0
            assert result["account"]["btc_balance"] == 0.9
            assert result["close_price"] == 55000.0

    @pytest.mark.asyncio
    async def test_close_trade_sell(self):
        """Test closing a sell trade order"""
        with patch('services.price_service.PriceService.fetch_live_price', return_value=55000.0):
            # Set up an open sell order
            mock_order = MagicMock(
                id=4,
                type="sell",
                amount=0.15,
                price=52000.0,
                created_at=datetime.datetime(2025, 3, 1, 15, 0, 0),
                closed_at=None,
                status="open"
            )
            self.mock_order_repo.get_open_order_by_id.return_value = mock_order

            # Set up account service for closing sell order
            mock_account = MagicMock(cash_balance=7000.0, btc_balance=0.7)
            self.mock_account_service.close_sell_order.return_value = mock_account

            # Simulate closing order update in repo
            mock_closed_order = MagicMock(
                id=4,
                type="sell",
                amount=0.15,
                price=52000.0,
                created_at=mock_order.created_at,
                closed_at=datetime.datetime(2025, 3, 1, 15, 5, 0),
                status="closed"
            )
            self.mock_order_repo.close_order.return_value = mock_closed_order

            result = await self.service.close_trade(4)

            self.mock_order_repo.get_open_order_by_id.assert_called_once_with(4)
            self.mock_account_service.close_sell_order.assert_called_once_with(0.15, 55000.0)
            self.mock_order_repo.close_order.assert_called_once_with(4)

            assert result["order_id"] == 4
            assert result["status"] == "closed"
            assert result["account"]["cash_balance"] == 7000.0
            assert result["account"]["btc_balance"] == 0.7
            assert result["close_price"] == 55000.0

    @pytest.mark.asyncio
    async def test_close_trade_not_found(self):
        """Test closing a trade that doesn't exist"""
        self.mock_order_repo.get_open_order_by_id.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            await self.service.close_trade(999)
        assert excinfo.value.status_code == 404
