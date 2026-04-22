from sqlalchemy.orm import Session
from app.models.item import Item, ItemRecipe


def get_items(
    db: Session,
    search: str | None = None,
    min_cost: int | None = None,
    max_cost: int | None = None,
) -> list[Item]:
    """Query items with optional search and cost filters."""
    query = db.query(Item)

    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
    if min_cost is not None:
        query = query.filter(Item.total_cost >= min_cost)
    if max_cost is not None:
        query = query.filter(Item.total_cost <= max_cost)

    return query.order_by(Item.total_cost).all()


def get_item_detail(db: Session, item_id: int) -> dict | None:
    """
    Get a single item with its recipe components and what it builds into.
    Returns None if the item doesn't exist.
    """
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        return None

    # Get components (what builds THIS item)
    components = (
        db.query(Item, ItemRecipe.qty)
        .join(ItemRecipe, ItemRecipe.component_item_id == Item.item_id)
        .filter(ItemRecipe.parent_item_id == item_id)
        .all()
    )

    # Get builds_into (what this item is a component OF)
    builds_into = (
        db.query(Item, ItemRecipe.qty)
        .join(ItemRecipe, ItemRecipe.parent_item_id == Item.item_id)
        .filter(ItemRecipe.component_item_id == item_id)
        .all()
    )

    return {
        "item": item,
        "components": [
            {"item_id": comp.item_id, "name": comp.name, "total_cost": comp.total_cost,
             "icon_url": comp.icon_url, "qty": qty}
            for comp, qty in components
        ],
        "builds_into": [
            {"item_id": parent.item_id, "name": parent.name, "total_cost": parent.total_cost,
             "icon_url": parent.icon_url, "qty": qty}
            for parent, qty in builds_into
        ],
    }
