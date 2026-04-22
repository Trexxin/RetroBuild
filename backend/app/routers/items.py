from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.item import ItemBase, ItemDetail, RecipeEntry
from app.services import item_service

router = APIRouter()


@router.get("", response_model=list[ItemBase])
def list_items(
    search: str | None = Query(None, description="Search items by name"),
    min_cost: int | None = Query(None, ge=0, description="Minimum gold cost"),
    max_cost: int | None = Query(None, ge=0, description="Maximum gold cost"),
    db: Session = Depends(get_db),
):
    """List all items with optional search and cost filters."""
    return item_service.get_items(db, search=search, min_cost=min_cost, max_cost=max_cost)


@router.get("/{item_id}", response_model=ItemDetail)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item details including recipe components and what it builds into."""
    result = item_service.get_item_detail(db, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")

    item = result["item"]
    return ItemDetail(
        item_id=item.item_id,
        name=item.name,
        total_cost=item.total_cost,
        purchasable=item.purchasable,
        icon_url=item.icon_url,
        description=item.description,
        version_tag=item.version_tag,
        components=[RecipeEntry(**c) for c in result["components"]],
        builds_into=[RecipeEntry(**b) for b in result["builds_into"]],
    )
