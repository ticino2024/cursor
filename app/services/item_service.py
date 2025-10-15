"""
Item service for business logic
"""
from typing import Optional, List
from datetime import datetime
import logging

from app.models.item import Item, items_db, ItemCategory, ItemStatus
from app.schemas.item import ItemCreate, ItemUpdate, ItemList, ItemSearch

logger = logging.getLogger(__name__)


class ItemService:
    """Service class for item-related operations"""
    
    def __init__(self):
        self.items = items_db  # In production, use database connection
    
    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_items(
        self,
        page: int = 1,
        page_size: int = 10,
        search_params: Optional[ItemSearch] = None
    ) -> ItemList:
        """Get paginated list of items with filters"""
        # Start with all items
        filtered_items = self.items.copy()
        
        if search_params:
            # Apply filters
            if search_params.category:
                filtered_items = [
                    item for item in filtered_items
                    if item.category == search_params.category
                ]
            
            if search_params.status:
                filtered_items = [
                    item for item in filtered_items
                    if item.status == search_params.status
                ]
            
            if search_params.min_price is not None:
                filtered_items = [
                    item for item in filtered_items
                    if item.price >= search_params.min_price
                ]
            
            if search_params.max_price is not None:
                filtered_items = [
                    item for item in filtered_items
                    if item.price <= search_params.max_price
                ]
            
            if search_params.query:
                query_lower = search_params.query.lower()
                filtered_items = [
                    item for item in filtered_items
                    if query_lower in item.name.lower()
                    or (item.description and query_lower in item.description.lower())
                ]
            
            if search_params.tags:
                # Filter by tags (items must have at least one matching tag)
                filtered_items = [
                    item for item in filtered_items
                    if any(tag in item.tags for tag in search_params.tags)
                ]
            
            if search_params.owner_id is not None:
                filtered_items = [
                    item for item in filtered_items
                    if item.owner_id == search_params.owner_id
                ]
        
        # Sort by updated_at (newest first)
        filtered_items.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Paginate
        total = len(filtered_items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = filtered_items[start_idx:end_idx]
        
        return ItemList(
            total=total,
            page=page,
            page_size=page_size,
            items=paginated_items
        )
    
    def search_items(self, query: str, limit: int = 10) -> List[Item]:
        """Search items by name, description, or tags"""
        query_lower = query.lower()
        matching_items = []
        
        for item in self.items:
            # Calculate relevance score
            score = 0
            
            # Exact match in name
            if query_lower == item.name.lower():
                score += 100
            # Partial match in name
            elif query_lower in item.name.lower():
                score += 50
            
            # Match in description
            if item.description and query_lower in item.description.lower():
                score += 20
            
            # Match in tags
            for tag in item.tags:
                if query_lower == tag.lower():
                    score += 30
                elif query_lower in tag.lower():
                    score += 10
            
            if score > 0:
                matching_items.append((score, item))
        
        # Sort by relevance score (descending) and return top results
        matching_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in matching_items[:limit]]
    
    def get_items_by_category(self, category: ItemCategory, limit: int = 10) -> List[Item]:
        """Get items by category"""
        category_items = [
            item for item in self.items
            if item.category == category
        ]
        # Sort by updated_at (newest first)
        category_items.sort(key=lambda x: x.updated_at, reverse=True)
        return category_items[:limit]
    
    def get_items_by_owner(self, owner_id: int, limit: int = 10) -> List[Item]:
        """Get items by owner"""
        owner_items = [
            item for item in self.items
            if item.owner_id == owner_id
        ]
        # Sort by updated_at (newest first)
        owner_items.sort(key=lambda x: x.updated_at, reverse=True)
        return owner_items[:limit]
    
    def create_item(self, item_data: ItemCreate) -> Item:
        """Create a new item"""
        # Generate new ID
        new_id = max([item.id for item in self.items], default=0) + 1
        
        # Create new item
        new_item = Item(
            id=new_id,
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            quantity=item_data.quantity,
            category=item_data.category,
            status=item_data.status or ItemStatus.AVAILABLE,
            tags=item_data.tags,
            metadata=item_data.metadata,
            owner_id=item_data.owner_id
        )
        
        # Add to database
        self.items.append(new_item)
        
        logger.info(f"Created new item: {new_item.name} (ID: {new_item.id})")
        return new_item
    
    def update_item(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Update item information"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        # Update fields if provided
        if item_update.name is not None:
            item.name = item_update.name
        
        if item_update.description is not None:
            item.description = item_update.description
        
        if item_update.price is not None:
            item.price = item_update.price
        
        if item_update.quantity is not None:
            item.quantity = item_update.quantity
        
        if item_update.category is not None:
            item.category = item_update.category
        
        if item_update.status is not None:
            item.status = item_update.status
        
        if item_update.tags is not None:
            item.tags = item_update.tags
        
        if item_update.metadata is not None:
            item.metadata = item_update.metadata
        
        # Update timestamp
        item.updated_at = datetime.now()
        
        logger.info(f"Updated item: {item.name} (ID: {item.id})")
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item"""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                deleted_item = self.items.pop(i)
                logger.info(f"Deleted item: {deleted_item.name} (ID: {deleted_item.id})")
                return True
        return False
    
    def update_item_quantity(self, item_id: int, quantity_change: int) -> Optional[Item]:
        """Update item quantity (for inventory management)"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        new_quantity = item.quantity + quantity_change
        if new_quantity < 0:
            logger.warning(f"Cannot reduce quantity below 0 for item {item.name}")
            return None
        
        item.quantity = new_quantity
        
        # Update status based on quantity
        if item.quantity == 0:
            item.status = ItemStatus.OUT_OF_STOCK
        elif item.status == ItemStatus.OUT_OF_STOCK and item.quantity > 0:
            item.status = ItemStatus.AVAILABLE
        
        item.updated_at = datetime.now()
        
        logger.info(f"Updated quantity for item {item.name}: {quantity_change:+d} (new: {item.quantity})")
        return item
    
    def get_available_items(self, limit: int = 10) -> List[Item]:
        """Get available items (in stock)"""
        available_items = [
            item for item in self.items
            if item.is_available()
        ]
        # Sort by updated_at (newest first)
        available_items.sort(key=lambda x: x.updated_at, reverse=True)
        return available_items[:limit]