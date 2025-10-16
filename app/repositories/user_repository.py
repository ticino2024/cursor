"""User repository for database operations."""

from typing import List, Optional
from sqlalchemy import select, update, delete, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User, UserRole


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_data: dict) -> User:
        """Create a new user.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            Created user object
        """
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        result = await self.session.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def update(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user.
        
        Args:
            user_id: User ID
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated user object or None if not found
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id, User.is_active == True)
            .values(**update_data)
        )
        await self.session.flush()
        return await self.get_by_id(user_id)
    
    async def soft_delete(self, user_id: str) -> bool:
        """Soft delete user by marking as inactive.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id, User.is_active == True)
            .values(is_active=False)
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """List users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter
            
        Returns:
            List of user objects
        """
        query = select(User).where(User.is_active == True)
        
        if role:
            query = query.where(User.role == role)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_users(self, role: Optional[UserRole] = None) -> int:
        """Count total number of users.
        
        Args:
            role: Optional role filter
            
        Returns:
            Total count of users
        """
        query = select(func.count(User.id)).where(User.is_active == True)
        
        if role:
            query = query.where(User.role == role)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name or email.
        
        Args:
            search_term: Search term to match against name or email
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching user objects
        """
        search_pattern = f"%{search_term}%"
        
        query = select(User).where(
            User.is_active == True,
            or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp.
        
        Args:
            user_id: User ID
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=func.now())
        )
        await self.session.flush()
    
    async def email_exists(self, email: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check if email already exists.
        
        Args:
            email: Email to check
            exclude_user_id: Optional user ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        query = select(User.id).where(User.email == email, User.is_active == True)
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
