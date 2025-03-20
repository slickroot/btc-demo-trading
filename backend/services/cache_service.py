import json
import redis.asyncio as redis
from config import REDIS_URL
from typing import Any, Optional

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL)
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache by key"""
        return await self.redis_client.get(key)
    
    async def set(self, key: str, value: Any, expire_seconds: int = None) -> bool:
        """Set a value in cache with optional expiration"""
        return await self.redis_client.set(key, value, ex=expire_seconds)
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        return await self.redis_client.delete(key)
    
    async def set_json(self, key: str, value: Any, expire_seconds: int = None) -> bool:
        """Serialize and store a JSON-serializable object"""
        json_value = json.dumps(value)
        return await self.set(key, json_value, expire_seconds)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize a JSON value from cache"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
