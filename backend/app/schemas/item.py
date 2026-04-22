from pydantic import BaseModel


class ItemBase(BaseModel):
    """Minimal item info used in lists and as nested references."""
    item_id: int
    name: str
    total_cost: int
    purchasable: bool
    icon_url: str | None = None

    class Config:
        from_attributes = True


class RecipeEntry(BaseModel):
    """A single component in a recipe, with quantity."""
    item_id: int
    name: str
    total_cost: int
    icon_url: str | None = None
    qty: int

    class Config:
        from_attributes = True


class ItemDetail(ItemBase):
    """Full item info including recipe breakdown and what it builds into."""
    description: str | None = None
    version_tag: str
    components: list[RecipeEntry] = []
    builds_into: list[RecipeEntry] = []
