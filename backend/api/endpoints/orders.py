from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from services.order_service import OrderService
from models.schemas import (
    TradeRequest, 
    CloseRequest, 
    TradeOrderResponse, 
    TradeResponse, 
    CloseResponse
)
from api.dependencies import get_order_service

router = APIRouter()

@router.get("/orders", response_model=List[TradeOrderResponse])
async def get_order_history(
    order_service: OrderService = Depends(get_order_service)
):
    """
    Returns the list of all trade orders.
    """
    return await order_service.get_order_history()

@router.post("/trade", response_model=TradeResponse)
async def create_trade(
    trade: TradeRequest,
    background_tasks: BackgroundTasks,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Creates a new trade order at the current live price.
    """
    # Inject background tasks into the service
    order_service.background_tasks = background_tasks
    
    return await order_service.create_trade(trade.type, trade.amount)

@router.post("/close", response_model=CloseResponse)
async def close_trade(
    close_req: CloseRequest,
    background_tasks: BackgroundTasks,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Closes an open trade order.
    """
    # Inject background tasks into the service
    order_service.background_tasks = background_tasks
    
    return await order_service.close_trade(close_req.order_id)
