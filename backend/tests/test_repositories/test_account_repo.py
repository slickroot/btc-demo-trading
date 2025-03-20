import pytest
from repositories.account_repo import AccountRepository
from models.db_models import Account

class TestAccountRepository:
    
    @pytest.mark.asyncio
    async def test_get_account_empty(self, setup_database, db_session):
        """Test getting account when none exists"""
        repo = AccountRepository(db_session)
        account = await repo.get_account()
        assert account is None
    
    @pytest.mark.asyncio
    async def test_create_account(self, setup_database, db_session):
        """Test creating a new account"""
        repo = AccountRepository(db_session)
        
        # Create a new account
        account = await repo.create_account(cash_balance=5000.0, btc_balance=0.5)
        
        # Verify the account was created
        assert account.id is not None
        assert account.cash_balance == 5000.0
        assert account.btc_balance == 0.5
        
        # Verify it's in the database
        result = await repo.get_account()
        assert result is not None
        assert result.cash_balance == 5000.0
        assert result.btc_balance == 0.5
    
    @pytest.mark.asyncio
    async def test_update_account_balances(self, setup_database, db_session, account_with_balance):
        """Test updating account balances"""
        repo = AccountRepository(db_session)
        
        # Update balances with positive deltas
        updated = await repo.update_account_balances(cash_delta=1000.0, btc_delta=0.25)
        assert updated.cash_balance == 11000.0  # 10000 + 1000
        assert updated.btc_balance == 1.25  # 1.0 + 0.25
        
        # Update with negative deltas
        updated = await repo.update_account_balances(cash_delta=-2000.0, btc_delta=-0.5)
        assert updated.cash_balance == 9000.0  # 11000 - 2000
        assert updated.btc_balance == 0.75  # 1.25 - 0.5
        
        # Verify changes are persisted
        account = await repo.get_account()
        assert account.cash_balance == 9000.0
        assert account.btc_balance == 0.75

    @pytest.mark.asyncio
    async def test_update_account_no_account(self, setup_database, db_session):
        """Test updating when no account exists should raise ValueError"""
        repo = AccountRepository(db_session)
        
        with pytest.raises(ValueError) as excinfo:
            await repo.update_account_balances(cash_delta=1000.0, btc_delta=0.1)
        
        assert "Account not initialized" in str(excinfo.value)
