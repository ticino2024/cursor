"""
User endpoints for the API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, status
from fastapi.responses import JSONResponse
import logging

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserList,
    UserLogin,
    Token
)
from app.models.user import users_db, User, UserRole, UserStatus
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "User not found"}}
)

# Initialize user service
user_service = UserService()


@router.get("", response_model=UserList, summary="Get all users")
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in username, email, or full name")
) -> UserList:
    """
    Retrieve a paginated list of users with optional filters.
    
    - **page**: Page number (starting from 1)
    - **page_size**: Number of items per page (max 100)
    - **role**: Filter by user role
    - **status**: Filter by user status
    - **search**: Search in username, email, or full name
    """
    try:
        result = user_service.get_users(
            page=page,
            page_size=page_size,
            role=role,
            status=status,
            search=search
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(
    user_id: int = Path(..., ge=1, description="User ID")
) -> UserResponse:
    """
    Get a specific user by their ID.
    
    - **user_id**: The ID of the user to retrieve
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create new user")
async def create_user(
    user_data: UserCreate = Body(..., description="User data for creation")
) -> UserResponse:
    """
    Create a new user account.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters)
    - **full_name**: User's full name (optional)
    - **role**: User role (defaults to 'user')
    """
    try:
        # Check if user already exists
        existing_user = user_service.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        existing_email = user_service.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = user_service.create_user(user_data)
        return UserResponse.model_validate(new_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.put("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(
    user_id: int = Path(..., ge=1, description="User ID"),
    user_update: UserUpdate = Body(..., description="User data for update")
) -> UserResponse:
    """
    Update user information.
    
    - **user_id**: The ID of the user to update
    - **user_update**: Fields to update (all optional)
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        # Check for username conflict if updating username
        if user_update.username and user_update.username != user.username:
            existing_user = user_service.get_user_by_username(user_update.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
        
        # Check for email conflict if updating email
        if user_update.email and user_update.email != user.email:
            existing_email = user_service.get_user_by_email(user_update.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        updated_user = user_service.update_user(user_id, user_update)
        return UserResponse.model_validate(updated_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
    user_id: int = Path(..., ge=1, description="User ID")
):
    """
    Delete a user account.
    
    - **user_id**: The ID of the user to delete
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        user_service.delete_user(user_id)
        return None
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )


@router.post("/login", response_model=Token, summary="User login")
async def login(
    credentials: UserLogin = Body(..., description="Login credentials")
) -> Token:
    """
    Authenticate user and receive access token.
    
    - **username**: Username or email
    - **password**: User password
    """
    # Mock authentication (in production, verify against hashed password)
    user = user_service.get_user_by_username(credentials.username)
    if not user:
        user = user_service.get_user_by_email(credentials.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Mock token generation (in production, use JWT)
    return Token(
        access_token="mock_token_" + user.username,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )


@router.get("/me/profile", response_model=UserResponse, summary="Get current user profile")
async def get_current_user(
    # In production, get current user from JWT token
    current_user_id: int = Query(1, description="Mock current user ID")
) -> UserResponse:
    """
    Get the profile of the currently authenticated user.
    
    In production, this would extract the user from the JWT token.
    """
    user = user_service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return UserResponse.model_validate(user)