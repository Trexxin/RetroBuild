from sqlalchemy.orm import Session
from app.models.build_plan import BuildPlan, BuildPlanTarget
from app.models.item import Item
from app.models.analysis import AnalysisRun, RunInventoryItem, RunPathStep
from app.schemas.analysis import AnalysisRunCreate
from app.services.graph_service import graph_service


class AnalysisError(Exception):
    """Raised when an analysis cannot be created (e.g. unknown plan)."""


def _build_response(db: Session, run: AnalysisRun) -> dict:
    """Hydrate a run row with the joined data the response schema needs."""
    plan = db.query(BuildPlan).filter(BuildPlan.plan_id == run.plan_id).first()
    plan_name = plan.name if plan else "(deleted plan)"

    inventory_items = [inv.item for inv in run.inventory]

    target_item = None
    if run.path_steps:
        last = run.path_steps[-1]
        target_item = last.item

    path_dicts = [
        {
            "step_num": s.step_num,
            "item_id": s.item_id,
            "item_name": s.item.name,
            "icon_url": s.item.icon_url,
            "step_cost": s.step_cost,
        }
        for s in run.path_steps
    ]

    total_cost = sum(s.step_cost for s in run.path_steps)
    gold_remaining = run.current_gold - total_cost

    message = None
    if not run.path_steps:
        message = (
            "None of your inventory items can be upgraded into a plan target."
        )

    return {
        "run_id": run.run_id,
        "plan_id": run.plan_id,
        "plan_name": plan_name,
        "current_gold": run.current_gold,
        "created_at": run.created_at,
        "inventory": inventory_items,
        "target_item": target_item,
        "path_steps": path_dicts,
        "total_path_cost": total_cost,
        "gold_remaining": gold_remaining,
        "message": message,
    }


def run_analysis(db: Session, payload: AnalysisRunCreate) -> dict:
    """Execute an analysis: graph search + persist the result."""
    plan = (
        db.query(BuildPlan).filter(BuildPlan.plan_id == payload.plan_id).first()
    )
    if not plan:
        raise AnalysisError(f"Plan {payload.plan_id} not found.")

    target_ids = [
        t.target_item_id
        for t in db.query(BuildPlanTarget)
        .filter(BuildPlanTarget.plan_id == payload.plan_id)
        .all()
    ]
    if not target_ids:
        raise AnalysisError("Plan has no target items.")

    # Filter out empty slots (None) and validate item ids exist
    inventory_ids = [i for i in payload.inventory_item_ids if i is not None]
    if inventory_ids:
        existing = {
            row.item_id
            for row in db.query(Item.item_id)
            .filter(Item.item_id.in_(inventory_ids))
            .all()
        }
        missing = [i for i in inventory_ids if i not in existing]
        if missing:
            raise AnalysisError(f"Unknown item IDs in inventory: {missing}")

    # Run the algorithm
    result = graph_service.find_optimal_path(
        inventory_item_ids=inventory_ids,
        target_item_ids=target_ids,
        current_gold=payload.current_gold,
    )

    # Persist the run
    run = AnalysisRun(
        plan_id=payload.plan_id,
        current_gold=payload.current_gold,
    )
    db.add(run)
    db.flush()  # Get run_id before inserting child rows

    for slot, item_id in enumerate(inventory_ids):
        db.add(
            RunInventoryItem(
                run_id=run.run_id, slot_index=slot, item_id=item_id
            )
        )

    for step_num, (item_id, step_cost) in enumerate(result["path"], start=1):
        db.add(
            RunPathStep(
                run_id=run.run_id,
                step_num=step_num,
                item_id=item_id,
                step_cost=step_cost,
            )
        )

    db.commit()
    db.refresh(run)  # Re-load to populate relationships

    response = _build_response(db, run)
    if result.get("message"):
        response["message"] = result["message"]
    return response


def get_run(db: Session, run_id: int) -> dict | None:
    run = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).first()
    if not run:
        return None
    return _build_response(db, run)


def list_history(db: Session, plan_id: int | None = None) -> list[dict]:
    query = db.query(AnalysisRun)
    if plan_id is not None:
        query = query.filter(AnalysisRun.plan_id == plan_id)
    runs = query.order_by(AnalysisRun.created_at.desc()).all()

    summaries = []
    for run in runs:
        plan = (
            db.query(BuildPlan)
            .filter(BuildPlan.plan_id == run.plan_id)
            .first()
        )
        target_name = None
        if run.path_steps:
            target_name = run.path_steps[-1].item.name
        total_cost = sum(s.step_cost for s in run.path_steps)
        summaries.append(
            {
                "run_id": run.run_id,
                "plan_id": run.plan_id,
                "plan_name": plan.name if plan else "(deleted plan)",
                "current_gold": run.current_gold,
                "created_at": run.created_at,
                "target_item_name": target_name,
                "total_path_cost": total_cost,
            }
        )
    return summaries


def delete_run(db: Session, run_id: int) -> bool:
    run = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).first()
    if not run:
        return False
    db.delete(run)  # cascade removes inventory + path_steps
    db.commit()
    return True
