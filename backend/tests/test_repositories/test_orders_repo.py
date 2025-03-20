import pytest
import datetime
from repositories.orders_repo import OrderRepository
from models.db_models import TradeOrder

class TestOrderRepository:
    
    @pytest.mark.asyncio
    async def test_get_all_orders_empty(self, setup_database, db_session):
        """Test getting all orders when none exist"""
        repo = OrderRepository(db_session)
        orders = await repo.get_all_orders()
        assert len(orders) == 0
    
    @pytest.mark.asyncio
    async def test_create_order(self, setup_database, db_session):
        """Test creating a new order"""
        repo = OrderRepository(db_session)
        
        # Create a new order
        order = await repo.create_order(type="buy", amount=0.1, price=50000.0)
        
        # Verify the order was created
        assert order.id is not None
        assert order.type == "buy"
        assert order.amount == 0.1
        assert order.price == 50000.0
        assert order.status == "open"
        assert order.created_at is not None
        assert order.closed_at is None
        
        # Verify it's in the database
        orders = await repo.get_all_orders()
        assert len(orders) == 1
        assert orders[0].id == order.id
    
    @pytest.mark.asyncio
    async def test_get_order_by_id(self, setup_database, db_session, sample_order):
        """Test getting a specific order by ID"""
        repo = OrderRepository(db_session)
        
        # Get the order by ID
        order = await repo.get_order_by_id(sample_order.id)
        
        # Verify it's the correct order
        assert order is not None
        assert order.id == sample_order.id
        assert order.type == "buy"
        assert order.amount == 0.1
        assert order.price == 50000.0
        
        # Test non-existent order
        non_existent = await repo.get_order_by_id(9999)
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_get_open_order_by_id(self, setup_database, db_session, sample_order):
        """Test getting an open order by ID"""
        repo = OrderRepository(db_session)
        
        # Get the open order
        order = await repo.get_open_order_by_id(sample_order.id)
        assert order is not None
        assert order.id == sample_order.id
        
        # Close the order
        sample_order.status = "closed"
        sample_order.closed_at = datetime.datetime.utcnow()
        db_session.add(sample_order)
        await db_session.commit()
        
        # Try to get it as an open order
        order = await repo.get_open_order_by_id(sample_order.id)
        assert order is None
    
    @pytest.mark.asyncio
    async def test_close_order(self, setup_database, db_session, sample_order):
        """Test closing an order"""
        repo = OrderRepository(db_session)
        
        # Close the order
        order = await repo.close_order(sample_order.id)
        
        # Verify it was closed
        assert order is not None
        assert order.status == "closed"
        assert order.closed_at is not None
        
        # Try to close it again
        order = await repo.close_order(sample_order.id)
        assert order is None  # Should return None since it's already closed
        
        # Try to close a non-existent order
        order = await repo.close_order(9999)
        assert order is None
