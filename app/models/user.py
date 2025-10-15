"""
User model definitions
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User:
    """
    User model (for demonstration - in production, use SQLAlchemy or similar ORM)
    """
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
        status: UserStatus = UserStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.last_login = last_login
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


# Mock database (in production, use a real database)
users_db: List[User] = [
    User(
        id=1,
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        role=UserRole.ADMIN
    ),
    User(
        id=2,
        username="john_doe",
        email="john@example.com",
        full_name="John Doe",
        role=UserRole.USER
    ),
    User(
        id=3,
        username="jane_smith",
        email="jane@example.com",
        full_name="Jane Smith",
        role=UserRole.MODERATOR
    )
]