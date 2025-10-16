"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.api.deps import get_user_service
from app.core.security import create_access_token, create_refresh_token, decode_token

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "User already exists"},
    },
)
async def register(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        user_service: User service
        
    Returns:
        Created user
    """
    user = await user_service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return JWT tokens",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    login_data: LoginRequest, user_service: UserService = Depends(get_user_service)
) -> TokenResponse:
    """
    Login user and return JWT tokens.
    
    Args:
        login_data: Login credentials
        user_service: User service
        
    Returns:
        JWT tokens
    """
    user = await user_service.authenticate_user(
        login_data.email, login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
    },
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """
    Refresh access token.
    
    Args:
        refresh_data: Refresh token data
        user_service: User service
        
    Returns:
        New JWT tokens
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists
    user = await user_service.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email to user",
    responses={
        200: {"description": "Password reset email sent"},
    },
)
async def forgot_password(
    reset_request: PasswordResetRequest,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Request password reset.
    
    Args:
        reset_request: Password reset request
        user_service: User service
        
    Returns:
        Success message
    """
    # Generate reset token
    token = await user_service.generate_password_reset_token(reset_request.email)

    # Note: In production, send email with reset link containing token
    # For now, we just return success message
    # Email would contain link like: https://yourapp.com/reset-password?token={token}

    return MessageResponse(
        message="If a user with that email exists, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset user password using reset token",
    responses={
        200: {"description": "Password reset successful"},
        400: {"description": "Invalid or expired token"},
    },
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Reset password using token.
    
    Args:
        reset_data: Password reset confirmation
        user_service: User service
        
    Returns:
        Success message
    """
    await user_service.reset_password(reset_data.token, reset_data.new_password)

    return MessageResponse(message="Password reset successful")
