"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageResponse
)
from app.services.user_service import UserService
from app.core.security import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user account."""
    service = UserService(db)
    return await service.create_user(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user with email and password, returns JWT tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"}
    }
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Login user and return authentication tokens."""
    service = UserService(db)
    return await service.authenticate_user(login_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Use refresh token to get a new access token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
        422: {"description": "Validation error"}
    }
)
async def refresh_token(
    token_data: RefreshTokenRequest
) -> TokenResponse:
    """Refresh access token using refresh token."""
    # Verify refresh token
    payload = verify_refresh_token(token_data.refresh_token)
    user_id: str = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send password reset email to user",
    responses={
        200: {"description": "Password reset email sent"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def forgot_password(
    request_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Request password reset."""
    # Note: In a real application, this would send an email
    # For now, we just return a success message
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset user password using reset token",
    responses={
        200: {"description": "Password reset successful"},
        401: {"description": "Invalid or expired token"},
        422: {"description": "Validation error"}
    }
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Reset user password."""
    # Note: In a real application, this would validate the reset token
    # and update the user's password
    return MessageResponse(
        message="Password has been reset successfully"
    )
