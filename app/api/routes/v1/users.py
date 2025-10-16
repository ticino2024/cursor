"""User management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate, UserSearchParams
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.user_service import UserService
from app.api.deps import get_user_service, get_current_user, require_role
import math

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Get paginated list of users (admin only)",
    responses={
        200: {"description": "Users retrieved successfully"},
        403: {"description": "Insufficient permissions"},
    },
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR)),
) -> PaginatedResponse[UserResponse]:
    """
    List users with pagination (admin/moderator only).
    
    Args:
        page: Page number
        size: Page size
        user_service: User service
        current_user: Current authenticated user
        
    Returns:
        Paginated list of users
    """
    skip = (page - 1) * size
    users = await user_service.list_users(skip=skip, limit=size)
    total = await user_service.count_users()
    pages = math.ceil(total / size)

    return PaginatedResponse(
        data=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/search",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Search users",
    description="Search users by name, email, or other criteria",
    responses={
        200: {"description": "Search results retrieved successfully"},
        403: {"description": "Insufficient permissions"},
    },
)
async def search_users(
    query: str = Query(None, description="Search query"),
    role: UserRole = Query(None, description="Filter by role"),
    is_active: bool = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR)),
) -> PaginatedResponse[UserResponse]:
    """
    Search users (admin/moderator only).
    
    Args:
        query: Search query
        role: Filter by role
        is_active: Filter by active status
        page: Page number
        size: Page size
        user_service: User service
        current_user: Current authenticated user
        
    Returns:
        Paginated search results
    """
    skip = (page - 1) * size
    users = await user_service.search_users(
        query=query, role=role, is_active=is_active, skip=skip, limit=size
    )

    # Count would need to be implemented in service for accurate pagination
    # For now, using the returned count
    total = len(users)
    pages = math.ceil(total / size) if total > 0 else 1

    return PaginatedResponse(
        data=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Get user details by ID",
    responses={
        200: {"description": "User retrieved successfully"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        user_service: User service
        current_user: Current authenticated user
        
    Returns:
        User details
    """
    # Users can only view their own profile unless they're admin/moderator
    if (
        current_user.id != user_id
        and current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]
    ):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    user = await user_service.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update user details",
    responses={
        200: {"description": "User updated successfully"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
        409: {"description": "Email already exists"},
    },
)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Update user.
    
    Args:
        user_id: User ID
        update_data: Update data
        user_service: User service
        current_user: Current authenticated user
        
    Returns:
        Updated user
    """
    # Users can only update their own profile unless they're admin
    # Only admins can change roles
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    # Only admins can change roles
    if update_data.role and current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user roles",
        )

    user = await user_service.update_user(user_id, update_data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Soft delete user (admin only)",
    responses={
        200: {"description": "User deleted successfully"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> MessageResponse:
    """
    Delete user (soft delete - admin only).
    
    Args:
        user_id: User ID
        user_service: User service
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    await user_service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
