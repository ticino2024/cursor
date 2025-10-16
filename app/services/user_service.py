"""User service for business logic."""

from typing import List, Optional
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    TokenResponse,
    UserLogin
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings
from app.utils.redis_client import redis_client
import json


class UserService:
    """Service for user-related business logic."""
    
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.session = session
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user response
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        if await self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password_hash"] = password_hash
        
        user = await self.repository.create(user_dict)
        await self.session.commit()
        
        # Invalidate cache
        await redis_client.delete("users:all")
        
        return UserResponse.model_validate(user)
    
    async def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Token response with access and refresh tokens
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = await self.repository.get_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        await self.repository.update_last_login(user.id)
        await self.session.commit()
        
        # Create tokens
        access_token = create_access_token({"sub": user.id, "role": user.role.value})
        refresh_token = create_refresh_token({"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User response
            
        Raises:
            HTTPException: If user not found
        """
        # Try to get from cache
        cache_key = f"user:{user_id}"
        cached_user = await redis_client.get(cache_key)
        
        if cached_user:
            return UserResponse(**cached_user)
        
        # Get from database
        user = await self.repository.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = UserResponse.model_validate(user)
        
        # Cache user data
        await redis_client.set(cache_key, user_response.model_dump(mode="json"))
        
        return user_response
    
    async def update_user(
        self,
        user_id: str,
        update_data: UserUpdate,
        current_user_id: str,
        current_user_role: UserRole
    ) -> UserResponse:
        """Update user.
        
        Args:
            user_id: User ID to update
            update_data: Update data
            current_user_id: ID of user making the request
            current_user_role: Role of user making the request
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found, unauthorized, or email already exists
        """
        # Check if user exists
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check authorization
        if current_user_role != UserRole.ADMIN and current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        
        # Non-admins cannot change their role
        if current_user_role != UserRole.ADMIN and update_data.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to change user role"
            )
        
        # Check if new email already exists
        if update_data.email:
            if await self.repository.email_exists(update_data.email, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
        
        # Update user
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_user = await self.repository.update(user_id, update_dict)
        await self.session.commit()
        
        # Invalidate cache
        await redis_client.delete(f"user:{user_id}")
        await redis_client.delete("users:all")
        
        return UserResponse.model_validate(updated_user)
    
    async def delete_user(
        self,
        user_id: str,
        current_user_id: str,
        current_user_role: UserRole
    ) -> None:
        """Delete (deactivate) user.
        
        Args:
            user_id: User ID to delete
            current_user_id: ID of user making the request
            current_user_role: Role of user making the request
            
        Raises:
            HTTPException: If user not found or unauthorized
        """
        # Check if user exists
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check authorization (admin or self)
        if current_user_role != UserRole.ADMIN and current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user"
            )
        
        # Soft delete user
        await self.repository.soft_delete(user_id)
        await self.session.commit()
        
        # Invalidate cache
        await redis_client.delete(f"user:{user_id}")
        await redis_client.delete("users:all")
    
    async def list_users(
        self,
        page: int = 1,
        size: int = 10,
        role: Optional[UserRole] = None
    ) -> tuple[List[UserResponse], int]:
        """List users with pagination.
        
        Args:
            page: Page number
            size: Page size
            role: Optional role filter
            
        Returns:
            Tuple of (list of users, total count)
        """
        skip = (page - 1) * size
        
        # Get users and count
        users = await self.repository.list_users(skip=skip, limit=size, role=role)
        total = await self.repository.count_users(role=role)
        
        user_responses = [UserResponse.model_validate(user) for user in users]
        
        return user_responses, total
    
    async def search_users(
        self,
        search_term: str,
        page: int = 1,
        size: int = 10
    ) -> List[UserResponse]:
        """Search users by name or email.
        
        Args:
            search_term: Search term
            page: Page number
            size: Page size
            
        Returns:
            List of matching users
        """
        skip = (page - 1) * size
        
        users = await self.repository.search_users(
            search_term=search_term,
            skip=skip,
            limit=size
        )
        
        return [UserResponse.model_validate(user) for user in users]
