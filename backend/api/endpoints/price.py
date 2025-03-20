from fastapi import APIRouter
from services.price_service import PriceService
from models.schemas import PriceResponse

router = APIRouter()

@router.get("/price", response_model=PriceResponse)
async def get_price():
    """
    Returns the current Bitcoin price.
    """
    price = await PriceService.fetch_live_price()
    return {"price": price}
