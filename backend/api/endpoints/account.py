from fastapi import APIRouter, Depends
from services.account_service import AccountService
from models.schemas import AccountResponse
from api.dependencies import get_account_service

router = APIRouter()

@router.get("/account", response_model=AccountResponse)
async def get_account(account_service: AccountService = Depends(get_account_service)):
    """
    Returns the account details including cash balance and BTC holdings.
    """
    account = await account_service.get_account_details()
    return {"cash_balance": account.cash_balance, "btc_balance": account.btc_balance}
