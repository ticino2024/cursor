"""
Item model definitions
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ItemStatus(str, Enum):
    """Item status enumeration"""
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    COMING_SOON = "coming_soon"


class ItemCategory(str, Enum):
    """Item category enumeration"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BOOKS = "books"
    HOME = "home"
    SPORTS = "sports"
    OTHER = "other"


class Item:
    """
    Item model (for demonstration - in production, use SQLAlchemy or similar ORM)
    """
    def __init__(
        self,
        id: int,
        name: str,
        description: Optional[str] = None,
        price: float = 0.0,
        quantity: int = 0,
        category: ItemCategory = ItemCategory.OTHER,
        status: ItemStatus = ItemStatus.AVAILABLE,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        owner_id: Optional[int] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.category = category
        self.status = status
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.owner_id = owner_id
    
    def to_dict(self) -> dict:
        """Convert item to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category.value,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner_id": self.owner_id
        }
    
    def is_available(self) -> bool:
        """Check if item is available"""
        return self.status == ItemStatus.AVAILABLE and self.quantity > 0


# Mock database (in production, use a real database)
items_db: List[Item] = [
    Item(
        id=1,
        name="Laptop Pro 15",
        description="High-performance laptop with 16GB RAM and 512GB SSD",
        price=1299.99,
        quantity=10,
        category=ItemCategory.ELECTRONICS,
        tags=["laptop", "computer", "electronics"],
        owner_id=1
    ),
    Item(
        id=2,
        name="Wireless Mouse",
        description="Ergonomic wireless mouse with long battery life",
        price=29.99,
        quantity=50,
        category=ItemCategory.ELECTRONICS,
        tags=["mouse", "wireless", "accessories"],
        owner_id=1
    ),
    Item(
        id=3,
        name="Python Programming Book",
        description="Comprehensive guide to Python programming",
        price=49.99,
        quantity=25,
        category=ItemCategory.BOOKS,
        tags=["python", "programming", "education"],
        owner_id=2
    ),
    Item(
        id=4,
        name="Running Shoes",
        description="Professional running shoes with advanced cushioning",
        price=89.99,
        quantity=0,
        category=ItemCategory.SPORTS,
        status=ItemStatus.OUT_OF_STOCK,
        tags=["shoes", "running", "sports"],
        owner_id=3
    )
]