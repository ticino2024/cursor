"""Shared dependencies for API endpoints."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.services.user_service import UserService
from app.core.security import decode_token

security = HTTPBearer()


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Get user service dependency.
    
    Args:
        db: Database session
        
    Returns:
        UserService instance
    """
    return UserService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Get current authenticated user.
    
    Args:
        credentials: Authorization credentials
        user_service: User service
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    # Decode token
    payload = decode_token(credentials.credentials)
    user_id: str = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency to require specific roles.
    
    Args:
        allowed_roles: Allowed user roles
        
    Returns:
        Dependency function
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has required role."""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
