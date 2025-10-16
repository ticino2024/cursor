"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.utils.redis_client import redis_client


router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is healthy and operational"
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "User Management API",
        "version": "1.0.0"
    }


@router.get(
    "/health/detailed",
    summary="Detailed health check",
    description="Check health of all components including database and Redis"
)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check endpoint."""
    health_status = {
        "status": "healthy",
        "service": "User Management API",
        "version": "1.0.0",
        "components": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if redis_client.redis:
            await redis_client.redis.ping()
            health_status["components"]["redis"] = "healthy"
        else:
            health_status["components"]["redis"] = "not connected"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
