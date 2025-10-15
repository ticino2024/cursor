"""
User service for business logic
"""
from typing import Optional, List
from datetime import datetime
import hashlib
import logging

from app.models.user import User, users_db, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserList

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations"""
    
    def __init__(self):
        self.users = users_db  # In production, use database connection
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def get_users(
        self,
        page: int = 1,
        page_size: int = 10,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> UserList:
        """Get paginated list of users with filters"""
        # Filter users
        filtered_users = self.users.copy()
        
        if role:
            filtered_users = [u for u in filtered_users if u.role == role]
        
        if status:
            filtered_users = [u for u in filtered_users if u.status == status]
        
        if search:
            search_lower = search.lower()
            filtered_users = [
                u for u in filtered_users
                if search_lower in u.username.lower()
                or search_lower in u.email.lower()
                or (u.full_name and search_lower in u.full_name.lower())
            ]
        
        # Paginate
        total = len(filtered_users)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_users = filtered_users[start_idx:end_idx]
        
        return UserList(
            total=total,
            page=page,
            page_size=page_size,
            users=paginated_users
        )
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Generate new ID
        new_id = max([u.id for u in self.users], default=0) + 1
        
        # Hash password (mock implementation)
        hashed_password = self._hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            id=new_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        # Add to database
        self.users.append(new_user)
        
        logger.info(f"Created new user: {new_user.username} (ID: {new_user.id})")
        return new_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields if provided
        if user_update.username:
            user.username = user_update.username
        
        if user_update.email:
            user.email = user_update.email
        
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        
        if user_update.role:
            user.role = user_update.role
        
        if user_update.status:
            user.status = user_update.status
        
        if user_update.password:
            # Update hashed password
            hashed_password = self._hash_password(user_update.password)
        
        # Update timestamp
        user.updated_at = datetime.now()
        
        logger.info(f"Updated user: {user.username} (ID: {user.id})")
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        for i, user in enumerate(self.users):
            if user.id == user_id:
                deleted_user = self.users.pop(i)
                logger.info(f"Deleted user: {deleted_user.username} (ID: {deleted_user.id})")
                return True
        return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        # Find user by username or email
        user = self.get_user_by_username(username)
        if not user:
            user = self.get_user_by_email(username)
        
        if not user:
            return None
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Verify password (mock implementation)
        # In production, compare with stored hashed password
        hashed_password = self._hash_password(password)
        # Mock verification - always returns the user for demo
        
        # Update last login
        user.last_login = datetime.now()
        
        return user
    
    def _hash_password(self, password: str) -> str:
        """Hash password (mock implementation)"""
        # In production, use bcrypt or similar secure hashing
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash (mock implementation)"""
        # In production, use bcrypt or similar secure hashing
        return self._hash_password(plain_password) == hashed_password