from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.item import ItemBase


class BuildPlanCreate(BaseModel):
    """Payload for creating a new plan."""
    name: str = Field(..., min_length=1, max_length=100)
    notes: str | None = None
    target_item_ids: list[int] = Field(..., min_length=1)


class BuildPlanUpdate(BaseModel):
    """Payload for updating an existing plan. All fields optional."""
    name: str | None = Field(None, min_length=1, max_length=100)
    notes: str | None = None
    target_item_ids: list[int] | None = Field(None, min_length=1)


class BuildPlanSummary(BaseModel):
    """Lightweight response for list views."""
    plan_id: int
    name: str
    notes: str | None
    target_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class BuildPlanResponse(BaseModel):
    """Full plan detail including target items."""
    plan_id: int
    name: str
    notes: str | None
    created_at: datetime
    targets: list[ItemBase]

    class Config:
        from_attributes = True
