"""Common schemas shared across the application."""

from datetime import datetime
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated response wrapper."""

    data: List[DataT] = Field(..., description="Response data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
