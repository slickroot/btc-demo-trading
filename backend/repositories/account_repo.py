from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import Account

class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_account(self) -> Account:
        """Get the account or None if it doesn't exist"""
        result = await self.session.execute(select(Account))
        return result.scalars().first()

    async def create_account(self, cash_balance: float = 10000.0, btc_balance: float = 0.5) -> Account:
        """Create a new account with initial balances"""
        account = Account(cash_balance=cash_balance, btc_balance=btc_balance)
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update_account_balances(self, cash_delta: float, btc_delta: float) -> Account:
        """Update account balances by the given deltas"""
        account = await self.get_account()
        if not account:
            raise ValueError("Account not initialized")
        
        account.cash_balance += cash_delta
        account.btc_balance += btc_delta
        
        await self.session.commit()
        await self.session.refresh(account)
        return account
