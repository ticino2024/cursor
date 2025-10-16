"""User profile endpoints."""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.db.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.api.deps import get_user_service, get_current_active_user

router = APIRouter()


@router.get(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Not authenticated"},
    },
)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user",
    responses={
        200: {"description": "Profile updated successfully"},
        401: {"description": "Not authenticated"},
        409: {"description": "Email already exists"},
    },
)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update current user profile.
    
    Args:
        update_data: Update data
        current_user: Current authenticated user
        user_service: User service
        
    Returns:
        Updated user profile
    """
    # Prevent users from changing their own role
    if update_data.role and update_data.role != current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role",
        )

    user = await user_service.update_user(current_user.id, update_data)
    return UserResponse.model_validate(user)


@router.post(
    "/avatar",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload profile avatar",
    description="Upload a profile avatar image",
    responses={
        200: {"description": "Avatar uploaded successfully"},
        401: {"description": "Not authenticated"},
        400: {"description": "Invalid file type or size"},
    },
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Upload profile avatar.
    
    Note: This is a placeholder implementation.
    In production, you would:
    1. Validate file type and size
    2. Upload to cloud storage (S3, etc.)
    3. Save the URL to the database
    
    Args:
        file: Avatar file
        current_user: Current authenticated user
        user_service: User service
        
    Returns:
        Success message
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed",
        )

    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    contents = await file.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit",
        )

    # In production, upload to cloud storage
    # For now, we'll just save a placeholder URL
    avatar_url = f"/static/avatars/{current_user.id}/{file.filename}"

    await user_service.update_avatar(current_user.id, avatar_url)

    return MessageResponse(message="Avatar uploaded successfully")
