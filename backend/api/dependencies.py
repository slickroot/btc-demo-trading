from fastapi import Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from config import async_session
from repositories.account_repo import AccountRepository
from repositories.orders_repo import OrderRepository
from services.account_service import AccountService
from services.cache_service import CacheService
from services.order_service import OrderService

# Database session dependency
async def get_db():
    """
    Create and yield a database session
    """
    async with async_session() as session:
        yield session

# Repository dependencies
async def get_account_repo(db: AsyncSession = Depends(get_db)):
    """Get the account repository"""
    return AccountRepository(db)

async def get_order_repo(db: AsyncSession = Depends(get_db)):
    """Get the order repository"""
    return OrderRepository(db)

# Service dependencies
def get_cache_service():
    """Get the cache service"""
    return CacheService()

async def get_account_service(account_repo: AccountRepository = Depends(get_account_repo)):
    """Get the account service"""
    return AccountService(account_repo)

async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repo),
    account_service: AccountService = Depends(get_account_service),
    cache_service: CacheService = Depends(get_cache_service),
    background_tasks: BackgroundTasks = None
):
    """Get the order service"""
    return OrderService(order_repo, account_service, cache_service, background_tasks)
