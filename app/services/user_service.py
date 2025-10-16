"""User service for business logic."""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import secrets

from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize user service.
        
        Args:
            db: Database session
        """
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If user with email already exists
        """
        # Check if user already exists
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        # Create user
        user = User(
            email=user_data.email.lower(),
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
            role=UserRole.USER,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: str, update_data: UserUpdate) -> User:
        """
        Update user.
        
        Args:
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check email uniqueness if being updated
        if update_data.email and update_data.email != user.email:
            existing_user = await self.get_by_email(update_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists",
                )

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        if "email" in update_dict:
            update_dict["email"] = update_dict["email"].lower()

        for field, value in update_dict.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.is_active = False
        await self.db.flush()

        return True

    async def list_users(
        self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = True
    ) -> List[User]:
        """
        List users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            
        Returns:
            List of users
        """
        query = select(User)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_users(self, is_active: Optional[bool] = True) -> int:
        """
        Count total users.
        
        Args:
            is_active: Filter by active status
            
        Returns:
            Total count
        """
        query = select(func.count(User.id))

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def search_users(
        self,
        query: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Search users.
        
        Args:
            query: Search query (name or email)
            role: Filter by role
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching users
        """
        stmt = select(User)

        if query:
            search_pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    User.name.ilike(search_pattern), User.email.ilike(search_pattern)
                )
            )

        if role:
            stmt = stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_by_email(email)
        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.flush()

        return user

    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """
        Generate password reset token.
        
        Args:
            email: User email
            
        Returns:
            Reset token if user found, None otherwise
        """
        user = await self.get_by_email(email)
        if not user:
            return None

        # Generate secure token
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

        await self.db.flush()

        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using token.
        
        Args:
            token: Reset token
            new_password: New password
            
        Returns:
            True if password reset successful
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        result = await self.db.execute(select(User).where(User.reset_token == token))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )

        if user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        # Update password
        user.password_hash = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None

        await self.db.flush()

        return True

    async def update_avatar(self, user_id: str, avatar_url: str) -> User:
        """
        Update user avatar.
        
        Args:
            user_id: User ID
            avatar_url: Avatar URL
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.avatar_url = avatar_url
        await self.db.flush()
        await self.db.refresh(user)

        return user
