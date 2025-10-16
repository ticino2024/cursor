"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is running",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return HealthResponse(status="healthy", version="1.0.0")
