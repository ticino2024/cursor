"""
Item schemas for request/response validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.item import ItemStatus, ItemCategory


class ItemBase(BaseModel):
    """Base item schema with common attributes"""
    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")
    price: float = Field(..., ge=0, description="Item price")
    quantity: int = Field(default=0, ge=0, description="Available quantity")
    category: ItemCategory = Field(default=ItemCategory.OTHER, description="Item category")
    tags: List[str] = Field(default_factory=list, description="Item tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Validate price to have maximum 2 decimal places"""
        return round(v, 2)


class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    status: Optional[ItemStatus] = Field(default=ItemStatus.AVAILABLE, description="Item status")
    owner_id: Optional[int] = Field(None, description="Owner user ID")


class ItemUpdate(BaseModel):
    """Schema for updating item information"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    category: Optional[ItemCategory] = None
    status: Optional[ItemStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(use_enum_values=True)
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Validate price to have maximum 2 decimal places"""
        if v is not None:
            return round(v, 2)
        return v


class ItemInDB(ItemBase):
    """Schema for item stored in database"""
    id: int
    status: ItemStatus
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ItemResponse(ItemBase):
    """Schema for item response"""
    id: int = Field(..., description="Item ID")
    status: ItemStatus = Field(..., description="Item availability status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    owner_id: Optional[int] = Field(None, description="Owner user ID")
    is_available: bool = Field(..., description="Whether item is available for purchase")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Laptop Pro 15",
                "description": "High-performance laptop",
                "price": 1299.99,
                "quantity": 10,
                "category": "electronics",
                "status": "available",
                "tags": ["laptop", "electronics"],
                "metadata": {"brand": "TechBrand", "warranty": "2 years"},
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "owner_id": 1,
                "is_available": True
            }
        }
    )
    
    @classmethod
    def model_validate(cls, obj: Any, *, strict: bool = None, from_attributes: bool = None, context: Dict[str, Any] = None):
        """Custom validation to add computed fields"""
        if hasattr(obj, 'is_available'):
            is_available = obj.is_available()
        else:
            is_available = obj.status == ItemStatus.AVAILABLE and obj.quantity > 0
        
        # Create a dict from the object and add the computed field
        if hasattr(obj, 'to_dict'):
            data = obj.to_dict()
        else:
            data = {
                'id': obj.id,
                'name': obj.name,
                'description': obj.description,
                'price': obj.price,
                'quantity': obj.quantity,
                'category': obj.category,
                'status': obj.status,
                'tags': obj.tags,
                'metadata': obj.metadata,
                'created_at': obj.created_at,
                'updated_at': obj.updated_at,
                'owner_id': obj.owner_id
            }
        data['is_available'] = is_available
        
        return super().model_validate(data, strict=strict, from_attributes=from_attributes, context=context)


class ItemList(BaseModel):
    """Schema for paginated item list"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    items: List[ItemResponse] = Field(..., description="List of items")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 50,
                "page": 1,
                "page_size": 10,
                "items": [
                    {
                        "id": 1,
                        "name": "Laptop Pro 15",
                        "description": "High-performance laptop",
                        "price": 1299.99,
                        "quantity": 10,
                        "category": "electronics",
                        "status": "available",
                        "tags": ["laptop"],
                        "created_at": "2024-01-01T12:00:00",
                        "updated_at": "2024-01-01T12:00:00",
                        "is_available": True
                    }
                ]
            }
        }
    )


class ItemSearch(BaseModel):
    """Schema for item search parameters"""
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[ItemCategory] = Field(None, description="Filter by category")
    status: Optional[ItemStatus] = Field(None, description="Filter by status")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    owner_id: Optional[int] = Field(None, description="Filter by owner")
    
    model_config = ConfigDict(use_enum_values=True)