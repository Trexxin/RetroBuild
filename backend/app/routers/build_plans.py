from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.build_plan import (
    BuildPlanCreate,
    BuildPlanUpdate,
    BuildPlanSummary,
    BuildPlanResponse,
)
from app.services import build_plan_service
from app.services.build_plan_service import ValidationError

router = APIRouter()


@router.get("", response_model=list[BuildPlanSummary])
def list_plans(db: Session = Depends(get_db)):
    """List all build plans, newest first."""
    return build_plan_service.list_plans(db)


@router.post("", response_model=BuildPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(payload: BuildPlanCreate, db: Session = Depends(get_db)):
    """Create a new build plan with target items."""
    try:
        plan_id = build_plan_service.create_plan(db, payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return build_plan_service.get_plan(db, plan_id)


@router.get("/{plan_id}", response_model=BuildPlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get full plan detail including target items."""
    plan = build_plan_service.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/{plan_id}", response_model=BuildPlanResponse)
def update_plan(
    plan_id: int, payload: BuildPlanUpdate, db: Session = Depends(get_db)
):
    """Update a plan's name, notes, or target items."""
    try:
        updated = build_plan_service.update_plan(db, plan_id, payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Plan not found")
    return build_plan_service.get_plan(db, plan_id)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a plan (and its targets via cascade)."""
    if not build_plan_service.delete_plan(db, plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
