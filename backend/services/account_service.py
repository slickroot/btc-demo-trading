from repositories.account_repo import AccountRepository
from fastapi import HTTPException

class AccountService:
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo
    
    async def get_account_details(self):
        """
        Get the current account details
        """
        account = await self.account_repo.get_account()
        if not account:
            raise HTTPException(status_code=404, detail="Account not initialized")
        return account
    
    async def check_buy_feasibility(self, trade_value: float):
        """
        Check if the account has enough cash for a buy trade
        """
        account = await self.account_repo.get_account()
        if not account:
            raise HTTPException(status_code=404, detail="Account not initialized")
        
        if account.cash_balance < trade_value:
            raise HTTPException(status_code=400, detail="Insufficient cash balance")
    
    async def check_sell_feasibility(self, btc_amount: float):
        """
        Check if the account has enough BTC for a sell trade
        """
        account = await self.account_repo.get_account()
        if not account:
            raise HTTPException(status_code=404, detail="Account not initialized")
        
        if account.btc_balance < btc_amount:
            raise HTTPException(status_code=400, detail="Insufficient BTC balance")
    
    async def process_buy(self, btc_amount: float, price: float):
        """
        Process a buy trade by updating account balances
        """
        trade_value = btc_amount * price
        await self.check_buy_feasibility(trade_value)
        return await self.account_repo.update_account_balances(-trade_value, btc_amount)
    
    async def process_sell(self, btc_amount: float, price: float):
        """
        Process a sell trade by updating account balances
        """
        trade_value = btc_amount * price
        await self.check_sell_feasibility(btc_amount)
        return await self.account_repo.update_account_balances(trade_value, -btc_amount)
    
    async def close_buy_order(self, btc_amount: float, price: float):
        """
        Close a buy order (sell the BTC)
        """
        trade_value = btc_amount * price
        await self.check_sell_feasibility(btc_amount)
        return await self.account_repo.update_account_balances(trade_value, -btc_amount)
    
    async def close_sell_order(self, btc_amount: float, price: float):
        """
        Close a sell order (buy back the BTC)
        """
        trade_value = btc_amount * price
        await self.check_buy_feasibility(trade_value)
        return await self.account_repo.update_account_balances(-trade_value, btc_amount)
