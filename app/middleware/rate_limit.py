"""Rate limiting middleware."""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.core.config import settings
from app.utils.redis_client import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Create rate limit key
        current_minute = int(time.time() / 60)
        rate_key = f"rate_limit:{client_ip}:{current_minute}"
        
        try:
            # Check current count
            current_count = await redis_client.get(rate_key)
            
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            # Check if limit exceeded
            if current_count >= settings.RATE_LIMIT_PER_MINUTE:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Increment counter
            await redis_client.increment(rate_key)
            await redis_client.expire(rate_key, 60)
            
        except HTTPException:
            raise
        except Exception as e:
            # If Redis fails, allow the request but log the error
            print(f"Rate limiting error: {e}")
        
        response = await call_next(request)
        return response
