import httpx
from fastapi import HTTPException

class PriceService:
    @staticmethod
    async def fetch_live_price() -> float:
        """
        Fetches the live Bitcoin price using the Coindesk API endpoint.
        """
        url = "https://data-api.coindesk.com/index/cc/v1/latest/tick?market=cadli&instruments=BTC-USD"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                data = response.json()
                price = float(data["Data"]["BTC-USD"]["VALUE"])
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error fetching live price")
        return price
