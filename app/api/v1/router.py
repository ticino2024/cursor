"""
API v1 router that combines all endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import users, items

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router)
api_router.include_router(items.router)

# You can add more routers here as your application grows
# api_router.include_router(auth.router)
# api_router.include_router(posts.router)
# api_router.include_router(comments.router)