"""Redis client for caching and rate limiting."""

from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    """Redis client wrapper."""

    def __init__(self):
        """Initialize Redis client."""
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.client = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.client:
            return None
        return await self.client.get(key)

    async def set(
        self, key: str, value: str, expire: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            
        Returns:
            True if successful
        """
        if not self.client:
            return False

        if expire:
            return await self.client.setex(key, expire, value)
        else:
            return await self.client.set(key, value)

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
        return await self.client.delete(key) > 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment value.
        
        Args:
            key: Cache key
            amount: Amount to increment
            
        Returns:
            New value
        """
        if not self.client:
            return 0
        return await self.client.incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
        return await self.client.expire(key, seconds)


# Global Redis client instance
redis_client = RedisClient()
