"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes.v1 import api_router
from app.db.session import init_db
from app.utils.redis_client import redis_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Args:
        app: FastAPI application
    """
    # Startup
    logger.info("Starting up application...")

    # Initialize database
    if settings.DEBUG:
        logger.info("Initializing database tables...")
        await init_db()

    # Connect to Redis
    logger.info("Connecting to Redis...")
    await redis_client.connect()

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Disconnect from Redis
    await redis_client.disconnect()

    logger.info("Application shut down successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive user management system with authentication, authorization, and user profile management capabilities.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Only add HSTS in production
    if settings.ENV == "production":
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"

    return response


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)

    # Get client IP
    client_ip = request.client.host

    # Skip rate limiting for health checks
    if request.url.path.startswith("/api/v1/health"):
        return await call_next(request)

    # Check rate limit
    rate_key = f"rate_limit:{client_ip}"

    try:
        # Get current count
        current_count = await redis_client.get(rate_key)

        if current_count is None:
            # First request
            await redis_client.set(rate_key, "1", expire=60)
        else:
            count = int(current_count)

            # Check if limit exceeded (60 requests per minute)
            if count >= 60:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please try again later.",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                    },
                )

            # Increment counter
            await redis_client.increment(rate_key)

    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # Continue on rate limiting errors

    return await call_next(request)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    logger.info(f"{request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code}"
    )

    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "User Management API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
