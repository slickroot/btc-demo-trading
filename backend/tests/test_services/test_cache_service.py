import pytest
import unittest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from services.cache_service import CacheService

class TestCacheService:
    
    def setup_method(self, method):
        self.mock_redis = AsyncMock()
        self.patch_redis = patch('redis.asyncio.from_url', return_value=self.mock_redis)
        self.patch_redis.start()
        self.cache_service = CacheService()
    
    def teardown_method(self, method):
        self.patch_redis.stop()
    
    @pytest.mark.asyncio
    async def test_get(self):
        """Test getting a value from cache"""
        self.mock_redis.get.return_value = "test_value"
        value = await self.cache_service.get("test_key")
        assert value == "test_value"
        self.mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_set(self):
        """Test setting a value in cache"""
        self.mock_redis.set.return_value = True
        result = await self.cache_service.set("test_key", "test_value", 60)
        assert result is True
        self.mock_redis.set.assert_called_once_with("test_key", "test_value", ex=60)
    
    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting a key from cache"""
        self.mock_redis.delete.return_value = 1
        result = await self.cache_service.delete("test_key")
        assert result == 1
        self.mock_redis.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_set_json(self):
        """Test setting a JSON value in cache"""
        self.mock_redis.set.return_value = True
        data = {"name": "test", "value": 123}
        
        result = await self.cache_service.set_json("test_key", data, 60)
        
        assert result is True
        self.mock_redis.set.assert_called_once()
        # Verify the data was serialized to JSON
        args, kwargs = self.mock_redis.set.call_args
        assert kwargs["ex"] == 60
        assert args[0] == "test_key"
        assert json.loads(args[1]) == data
    
    @pytest.mark.asyncio
    async def test_get_json(self):
        """Test getting and deserializing a JSON value from cache"""
        data = {"name": "test", "value": 123}
        self.mock_redis.get.return_value = json.dumps(data)
        
        result = await self.cache_service.get_json("test_key")
        
        assert result == data
        self.mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_json_none(self):
        """Test get_json when key doesn't exist"""
        self.mock_redis.get.return_value = None
        
        result = await self.cache_service.get_json("non_existent_key")
        
        assert result is None
        self.mock_redis.get.assert_called_once_with("non_existent_key")
