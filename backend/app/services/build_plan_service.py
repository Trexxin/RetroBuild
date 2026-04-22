from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.build_plan import BuildPlan, BuildPlanTarget
from app.models.item import Item
from app.schemas.build_plan import BuildPlanCreate, BuildPlanUpdate


class ValidationError(Exception):
    """Raised when input references items that don't exist."""


def _validate_target_ids(db: Session, target_item_ids: list[int]) -> None:
    """Ensure all given item IDs exist in the items table."""
    unique_ids = set(target_item_ids)
    found = db.query(Item.item_id).filter(Item.item_id.in_(unique_ids)).all()
    found_ids = {row.item_id for row in found}
    missing = unique_ids - found_ids
    if missing:
        raise ValidationError(f"Unknown item IDs: {sorted(missing)}")


def list_plans(db: Session) -> list[dict]:
    """Return lightweight plan summaries ordered by newest first."""
    rows = (
        db.query(
            BuildPlan.plan_id,
            BuildPlan.name,
            BuildPlan.notes,
            BuildPlan.created_at,
            func.count(BuildPlanTarget.target_item_id).label("target_count"),
        )
        .outerjoin(BuildPlanTarget, BuildPlanTarget.plan_id == BuildPlan.plan_id)
        .group_by(BuildPlan.plan_id)
        .order_by(BuildPlan.created_at.desc())
        .all()
    )
    return [
        {
            "plan_id": row.plan_id,
            "name": row.name,
            "notes": row.notes,
            "target_count": row.target_count,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def get_plan(db: Session, plan_id: int) -> dict | None:
    """Return a single plan with its target items, or None if missing."""
    plan = db.query(BuildPlan).filter(BuildPlan.plan_id == plan_id).first()
    if not plan:
        return None

    # Load target Items via the junction table
    targets = (
        db.query(Item)
        .join(BuildPlanTarget, BuildPlanTarget.target_item_id == Item.item_id)
        .filter(BuildPlanTarget.plan_id == plan_id)
        .order_by(Item.total_cost)
        .all()
    )
    return {
        "plan_id": plan.plan_id,
        "name": plan.name,
        "notes": plan.notes,
        "created_at": plan.created_at,
        "targets": targets,
    }


def create_plan(db: Session, payload: BuildPlanCreate) -> int:
    """Create a plan with targets. Returns the new plan_id."""
    _validate_target_ids(db, payload.target_item_ids)

    plan = BuildPlan(name=payload.name, notes=payload.notes)
    db.add(plan)
    db.flush()  # Get plan_id before inserting targets

    for item_id in set(payload.target_item_ids):  # de-dupe
        db.add(BuildPlanTarget(plan_id=plan.plan_id, target_item_id=item_id))

    db.commit()
    return plan.plan_id


def update_plan(db: Session, plan_id: int, payload: BuildPlanUpdate) -> bool:
    """Update a plan's name/notes/targets. Returns True if updated, False if not found."""
    plan = db.query(BuildPlan).filter(BuildPlan.plan_id == plan_id).first()
    if not plan:
        return False

    if payload.name is not None:
        plan.name = payload.name
    if payload.notes is not None:
        plan.notes = payload.notes

    if payload.target_item_ids is not None:
        _validate_target_ids(db, payload.target_item_ids)
        # Replace target set
        db.query(BuildPlanTarget).filter(
            BuildPlanTarget.plan_id == plan_id
        ).delete()
        for item_id in set(payload.target_item_ids):
            db.add(BuildPlanTarget(plan_id=plan_id, target_item_id=item_id))

    db.commit()
    return True


def delete_plan(db: Session, plan_id: int) -> bool:
    """Delete a plan. Returns True if deleted, False if not found."""
    plan = db.query(BuildPlan).filter(BuildPlan.plan_id == plan_id).first()
    if not plan:
        return False
    db.delete(plan)  # cascade handles targets
    db.commit()
    return True
