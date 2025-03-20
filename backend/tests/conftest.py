import asyncio
import unittest
import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

# Import your app modules
from models.db_models import Base, Account, TradeOrder
from main import app

# Set up test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# Test fixtures
@pytest.fixture
async def setup_database():
    """Set up test database with tables"""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop all tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """Create a fresh database session for each test"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_price_service():
    """Mock for price service that returns a fixed price"""
    with patch('services.price_service.PriceService.fetch_live_price', 
               new_callable=AsyncMock, return_value=50000.0):
        yield

@pytest.fixture
def mock_cache_service():
    """Mock for cache service"""
    cache_service = AsyncMock()
    cache_service.get_json = AsyncMock(return_value=None)
    cache_service.set_json = AsyncMock(return_value=True)
    cache_service.delete = AsyncMock(return_value=True)
    return cache_service

@pytest.fixture
async def account_with_balance(db_session):
    """Create an account with predefined balance"""
    account = Account(cash_balance=10000.0, btc_balance=1.0)
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def sample_order(db_session):
    """Create a sample open buy order"""
    order = TradeOrder(type="buy", amount=0.1, price=50000.0, status="open")
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order

# Helper class for running async tests with unittest
class AsyncTestCase(unittest.TestCase):
    """Base class for async tests with unittest"""
    def run_async(self, coro):
        return asyncio.run(coro)
