from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.item import ItemBase


class AnalysisRunCreate(BaseModel):
    """Payload for running a new analysis."""
    plan_id: int
    current_gold: int = Field(..., ge=0)
    # 0–6 inventory items (None means empty slot in 6-slot UI but can accept the bare list)
    inventory_item_ids: list[int] = Field(default_factory=list, max_length=6)


class PathStep(BaseModel):
    """A single step on the recommended purchase path."""
    step_num: int
    item_id: int
    item_name: str
    icon_url: str | None = None
    step_cost: int  # Gold spent at this step

    class Config:
        from_attributes = True


class AnalysisRunResponse(BaseModel):
    """Full result of an analysis."""
    run_id: int
    plan_id: int
    plan_name: str
    current_gold: int
    created_at: datetime
    inventory: list[ItemBase]
    # The recommended target reached by following path_steps:
    target_item: ItemBase | None
    path_steps: list[PathStep]
    total_path_cost: int
    gold_remaining: int  # current_gold - total_path_cost (can be negative = need more)
    message: str | None = None

    class Config:
        from_attributes = True


class AnalysisRunSummary(BaseModel):
    """Lightweight summary for the history list."""
    run_id: int
    plan_id: int
    plan_name: str
    current_gold: int
    created_at: datetime
    target_item_name: str | None
    total_path_cost: int

    class Config:
        from_attributes = True
