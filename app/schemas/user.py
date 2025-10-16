"""User schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re

from app.db.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name contains only letters, spaces, and basic punctuation."""
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, and apostrophes"
            )
        return v.strip()


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """Schema for user update."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="User full name"
    )
    role: Optional[UserRole] = Field(None, description="User role")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name if provided."""
        if v is not None:
            if not re.match(r"^[a-zA-Z\s\-']+$", v):
                raise ValueError(
                    "Name can only contain letters, spaces, hyphens, and apostrophes"
                )
            return v.strip()
        return v


class UserResponse(UserBase):
    """Schema for user response."""

    id: str = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")
    email_verified: bool = Field(..., description="Whether email is verified")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserInDB(UserResponse):
    """Schema for user in database (includes password hash)."""

    password_hash: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserSearchParams(BaseModel):
    """Schema for user search parameters."""

    query: Optional[str] = Field(None, description="Search query")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
