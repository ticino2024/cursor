"""User management endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse
from app.services.user_service import UserService
from app.api.deps import get_current_active_user, require_admin
import math


router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users",
    description="Get paginated list of all users (admin only)",
    dependencies=[Depends(require_admin)],
    responses={
        200: {"description": "Users retrieved successfully"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"}
    }
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[UserResponse]:
    """List all users with pagination (admin only)."""
    service = UserService(db)
    users, total = await service.list_users(page=page, size=size, role=role)
    
    return PaginatedResponse(
        data=users,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user (admin only)",
    dependencies=[Depends(require_admin)],
    responses={
        201: {"description": "User created successfully"},
        403: {"description": "Insufficient permissions"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Create a new user (admin only)."""
    service = UserService(db)
    return await service.create_user(user_data)


@router.get(
    "/search",
    response_model=list[UserResponse],
    summary="Search users",
    description="Search users by name or email (admin only)",
    dependencies=[Depends(require_admin)],
    responses={
        200: {"description": "Search results retrieved successfully"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"}
    }
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
) -> list[UserResponse]:
    """Search users by name or email (admin only)."""
    service = UserService(db)
    return await service.search_users(search_term=q, page=page, size=size)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get detailed information about a specific user",
    responses={
        200: {"description": "User retrieved successfully"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Get user by ID."""
    service = UserService(db)
    return await service.get_user_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information",
    responses={
        200: {"description": "User updated successfully"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Update user information."""
    service = UserService(db)
    return await service.update_user(
        user_id=user_id,
        update_data=update_data,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Soft delete user (mark as inactive)",
    responses={
        204: {"description": "User deleted successfully"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"}
    }
)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """Delete (deactivate) user."""
    service = UserService(db)
    await service.delete_user(
        user_id=user_id,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )
