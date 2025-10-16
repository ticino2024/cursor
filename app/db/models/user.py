"""User database model."""

from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func

from app.db.base import BaseModel


class UserRole(str, PyEnum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(BaseModel):
    """User database model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(
        Enum(UserRole, native_enum=False, length=50),
        default=UserRole.USER,
        nullable=False,
    )
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
