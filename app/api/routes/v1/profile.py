"""User profile endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PasswordChange, MessageResponse
from app.services.user_service import UserService
from app.api.deps import get_current_active_user
from app.core.security import verify_password, get_password_hash
from app.repositories.user_repository import UserRepository


router = APIRouter()


@router.get(
    "",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get profile information for the currently authenticated user",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Not authenticated"}
    }
)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.put(
    "",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update profile information for the currently authenticated user",
    responses={
        200: {"description": "Profile updated successfully"},
        401: {"description": "Not authenticated"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
async def update_profile(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Update current user profile."""
    service = UserService(db)
    return await service.update_user(
        user_id=current_user.id,
        update_data=update_data,
        current_user_id=current_user.id,
        current_user_role=current_user.role
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change password for the currently authenticated user",
    responses={
        200: {"description": "Password changed successfully"},
        401: {"description": "Invalid current password"},
        422: {"description": "Validation error"}
    }
)
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MessageResponse:
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Update password
    repository = UserRepository(db)
    new_password_hash = get_password_hash(password_data.new_password)
    await repository.update(current_user.id, {"password_hash": new_password_hash})
    await db.commit()
    
    return MessageResponse(message="Password changed successfully")


from fastapi import HTTPException, status
