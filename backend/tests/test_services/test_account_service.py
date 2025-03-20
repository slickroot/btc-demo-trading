import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from services.account_service import AccountService
from models.db_models import Account

class TestAccountService:
    
    def setup_method(self, method):
        self.mock_repo = AsyncMock()
        self.service = AccountService(self.mock_repo)
    
    @pytest.mark.asyncio
    async def test_get_account_details_success(self):
        """Test getting account details when account exists"""
        mock_account = Account(id=1, cash_balance=10000.0, btc_balance=1.0)
        self.mock_repo.get_account.return_value = mock_account
        
        account = await self.service.get_account_details()
        
        assert account is mock_account
        self.mock_repo.get_account.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_account_details_not_found(self):
        """Test getting account details when account doesn't exist"""
        self.mock_repo.get_account.return_value = None
        
        with pytest.raises(HTTPException) as excinfo:
            await self.service.get_account_details()
        
        assert excinfo.value.status_code == 404
        assert "Account not initialized" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_check_buy_feasibility_sufficient_funds(self):
        """Test buy feasibility check with sufficient funds"""
        mock_account = Account(id=1, cash_balance=10000.0, btc_balance=1.0)
        self.mock_repo.get_account.return_value = mock_account
        
        # Should not raise an exception
        await self.service.check_buy_feasibility(5000.0)
        self.mock_repo.get_account.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_buy_feasibility_insufficient_funds(self):
        """Test buy feasibility check with insufficient funds"""
        mock_account = Account(id=1, cash_balance=5000.0, btc_balance=1.0)
        self.mock_repo.get_account.return_value = mock_account
        
        with pytest.raises(HTTPException) as excinfo:
            await self.service.check_buy_feasibility(10000.0)
        
        assert excinfo.value.status_code == 400
        assert "Insufficient cash balance" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_check_sell_feasibility_sufficient_btc(self):
        """Test sell feasibility check with sufficient BTC"""
        mock_account = Account(id=1, cash_balance=10000.0, btc_balance=1.0)
        self.mock_repo.get_account.return_value = mock_account
        
        # Should not raise an exception
        await self.service.check_sell_feasibility(0.5)
        self.mock_repo.get_account.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_sell_feasibility_insufficient_btc(self):
        """Test sell feasibility check with insufficient BTC"""
        mock_account = Account(id=1, cash_balance=10000.0, btc_balance=0.1)
        self.mock_repo.get_account.return_value = mock_account
        
        with pytest.raises(HTTPException) as excinfo:
            await self.service.check_sell_feasibility(0.5)
        
        assert excinfo.value.status_code == 400
        assert "Insufficient BTC balance" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_process_buy(self):
        """Test processing a buy order"""
        mock_account = Account(id=1, cash_balance=10000.0, btc_balance=1.0)
        self.mock_repo.get_account.return_value = mock_account
        self.mock_repo.update_account_balances.return_value = mock_account
        
        result = await self.service.process_buy(0.1, 50000.0)
        
        assert result is mock_account
        # Check that update was called with correct deltas
        self.mock_repo.update_account_balances.assert_called_once_with(-5000.0, 0.1)
    
    @pytest.mark.asyncio
    async def test_process_sell(self):
        """Test processing a sell order"""
        mock_account = Account(id=1, cash_balance=15000.0, btc_balance=0.9)
        self.mock_repo.get_account.return_value = mock_account
        self.mock_repo.update_account_balances.return_value = mock_account
        
        result = await self.service.process_sell(0.1, 50000.0)
        
        assert result is mock_account
        # Check that update was called with correct deltas
        self.mock_repo.update_account_balances.assert_called_once_with(5000.0, -0.1)
