"""
Item endpoints for the API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, status
import logging

from app.schemas.item import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemList,
    ItemSearch
)
from app.models.item import items_db, Item, ItemCategory, ItemStatus
from app.services.item_service import ItemService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/items",
    tags=["Items"],
    responses={404: {"description": "Item not found"}}
)

# Initialize item service
item_service = ItemService()


@router.get("", response_model=ItemList, summary="Get all items")
async def get_items(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[ItemCategory] = Query(None, description="Filter by category"),
    status: Optional[ItemStatus] = Query(None, description="Filter by status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID")
) -> ItemList:
    """
    Retrieve a paginated list of items with optional filters.
    
    - **page**: Page number (starting from 1)
    - **page_size**: Number of items per page (max 100)
    - **category**: Filter by item category
    - **status**: Filter by item status
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **search**: Search in item name and description
    - **owner_id**: Filter by owner user ID
    """
    try:
        search_params = ItemSearch(
            category=category,
            status=status,
            min_price=min_price,
            max_price=max_price,
            query=search,
            owner_id=owner_id
        )
        
        result = item_service.get_items(
            page=page,
            page_size=page_size,
            search_params=search_params
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching items"
        )


@router.get("/search", response_model=List[ItemResponse], summary="Search items")
async def search_items(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
) -> List[ItemResponse]:
    """
    Search for items by name, description, or tags.
    
    - **q**: Search query (searches in name, description, and tags)
    - **limit**: Maximum number of results to return
    """
    try:
        items = item_service.search_items(query=q, limit=limit)
        return [ItemResponse.model_validate(item) for item in items]
    except Exception as e:
        logger.error(f"Error searching items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching items"
        )


@router.get("/{item_id}", response_model=ItemResponse, summary="Get item by ID")
async def get_item(
    item_id: int = Path(..., ge=1, description="Item ID")
) -> ItemResponse:
    """
    Get a specific item by its ID.
    
    - **item_id**: The ID of the item to retrieve
    """
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return ItemResponse.model_validate(item)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create new item")
async def create_item(
    item_data: ItemCreate = Body(..., description="Item data for creation"),
    current_user_id: int = Query(1, description="Mock current user ID")  # In production, get from JWT
) -> ItemResponse:
    """
    Create a new item.
    
    - **name**: Item name (required)
    - **description**: Item description (optional)
    - **price**: Item price (required, >= 0)
    - **quantity**: Available quantity (default: 0)
    - **category**: Item category
    - **tags**: List of tags
    - **metadata**: Additional metadata as key-value pairs
    """
    try:
        # Set owner_id if not provided
        if item_data.owner_id is None:
            item_data.owner_id = current_user_id
        
        new_item = item_service.create_item(item_data)
        return ItemResponse.model_validate(new_item)
    
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating item"
        )


@router.put("/{item_id}", response_model=ItemResponse, summary="Update item")
async def update_item(
    item_id: int = Path(..., ge=1, description="Item ID"),
    item_update: ItemUpdate = Body(..., description="Item data for update"),
    current_user_id: int = Query(1, description="Mock current user ID")  # In production, get from JWT
) -> ItemResponse:
    """
    Update item information.
    
    - **item_id**: The ID of the item to update
    - **item_update**: Fields to update (all optional)
    """
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Check ownership (in production, implement proper authorization)
    if item.owner_id and item.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this item"
        )
    
    try:
        updated_item = item_service.update_item(item_id, item_update)
        return ItemResponse.model_validate(updated_item)
    
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating item"
        )


@router.patch("/{item_id}/status", response_model=ItemResponse, summary="Update item status")
async def update_item_status(
    item_id: int = Path(..., ge=1, description="Item ID"),
    status: ItemStatus = Body(..., description="New status"),
    current_user_id: int = Query(1, description="Mock current user ID")  # In production, get from JWT
) -> ItemResponse:
    """
    Quick update for item status.
    
    - **item_id**: The ID of the item to update
    - **status**: New status value
    """
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Check ownership
    if item.owner_id and item.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this item"
        )
    
    try:
        item.status = status
        return ItemResponse.model_validate(item)
    
    except Exception as e:
        logger.error(f"Error updating item status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating item status"
        )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item")
async def delete_item(
    item_id: int = Path(..., ge=1, description="Item ID"),
    current_user_id: int = Query(1, description="Mock current user ID")  # In production, get from JWT
):
    """
    Delete an item.
    
    - **item_id**: The ID of the item to delete
    """
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Check ownership
    if item.owner_id and item.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this item"
        )
    
    try:
        item_service.delete_item(item_id)
        return None
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting item"
        )


@router.get("/category/{category}", response_model=List[ItemResponse], summary="Get items by category")
async def get_items_by_category(
    category: ItemCategory = Path(..., description="Item category"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items")
) -> List[ItemResponse]:
    """
    Get items by specific category.
    
    - **category**: The category to filter by
    - **limit**: Maximum number of items to return
    """
    try:
        items = item_service.get_items_by_category(category, limit)
        return [ItemResponse.model_validate(item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching items by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching items"
        )


@router.get("/owner/{owner_id}", response_model=List[ItemResponse], summary="Get items by owner")
async def get_items_by_owner(
    owner_id: int = Path(..., ge=1, description="Owner user ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items")
) -> List[ItemResponse]:
    """
    Get all items owned by a specific user.
    
    - **owner_id**: The ID of the owner
    - **limit**: Maximum number of items to return
    """
    try:
        items = item_service.get_items_by_owner(owner_id, limit)
        return [ItemResponse.model_validate(item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching items by owner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching items"
        )