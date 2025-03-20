import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from services.price_service import PriceService

class TestPriceService:
    
    @pytest.mark.asyncio
    async def test_fetch_live_price_success(self):
        """Test successful price fetch"""
        mock_response = AsyncMock()
        # Override .json with a normal function that returns the dict
        mock_response.json = MagicMock(return_value={
            "Data": {
                "BTC-USD": {
                    "VALUE": "50000.0"
                }
            }
        })
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            price = await PriceService.fetch_live_price()
            assert price == 50000.0
    
    @pytest.mark.asyncio
    async def test_fetch_live_price_http_error(self):
        """Test handling HTTP errors"""
        with patch('httpx.AsyncClient.get', side_effect=httpx.HTTPError("Error")):
            with pytest.raises(HTTPException) as excinfo:
                await PriceService.fetch_live_price()
            assert excinfo.value.status_code == 500
            assert "Error fetching live price" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_fetch_live_price_json_error(self):
        """Test handling JSON parsing errors"""
        mock_response = AsyncMock()
        # Make .json() raise a ValueError instead of returning a coroutine
        mock_response.json = MagicMock(side_effect=ValueError("Invalid JSON"))
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            with pytest.raises(HTTPException) as excinfo:
                await PriceService.fetch_live_price()
            assert excinfo.value.status_code == 500
            assert "Error fetching live price" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_fetch_live_price_missing_data(self):
        """Test handling missing data in response"""
        mock_response = AsyncMock()
        mock_response.json = MagicMock(return_value={"Data": {}})  # Missing BTC-USD data
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            with pytest.raises(HTTPException) as excinfo:
                await PriceService.fetch_live_price()
            assert excinfo.value.status_code == 500
            assert "Error fetching live price" in excinfo.value.detail
