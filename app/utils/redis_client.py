"""Redis client for caching and session storage."""

import json
from typing import Optional, Any
import redis.asyncio as aioredis

from app.core.config import settings


class RedisClient:
    """Redis client wrapper for caching operations."""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        if not self.redis:
            return None
        
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in Redis."""
        if not self.redis:
            return False
        
        if expire is None:
            expire = settings.REDIS_CACHE_EXPIRE
        
        # Serialize value to JSON if not string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        await self.redis.set(key, value, ex=expire)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        if not self.redis:
            return False
        
        await self.redis.delete(key)
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.redis:
            return False
        
        return await self.redis.exists(key) > 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in Redis."""
        if not self.redis:
            return 0
        
        return await self.redis.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        if not self.redis:
            return False
        
        return await self.redis.expire(key, seconds)


# Global Redis client instance
redis_client = RedisClient()
