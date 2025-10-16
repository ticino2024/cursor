"""Common schemas used across the application."""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    data: List[T] = Field(..., description="Response data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(None, description="Error code")


class MessageResponse(BaseModel):
    """Standard message response."""
    
    message: str = Field(..., description="Response message")
