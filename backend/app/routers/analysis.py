from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analysis import (
    AnalysisRunCreate,
    AnalysisRunResponse,
    AnalysisRunSummary,
)
from app.services import analysis_service
from app.services.analysis_service import AnalysisError

router = APIRouter()


@router.post(
    "/run",
    response_model=AnalysisRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_analysis(payload: AnalysisRunCreate, db: Session = Depends(get_db)):
    """Run an analysis and persist the result."""
    try:
        return analysis_service.run_analysis(db, payload)
    except AnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=list[AnalysisRunSummary])
def history(
    plan_id: int | None = Query(None, description="Filter to a specific plan"),
    db: Session = Depends(get_db),
):
    """List past analysis runs, newest first."""
    return analysis_service.list_history(db, plan_id=plan_id)


@router.get("/history/{run_id}", response_model=AnalysisRunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    """Get full detail for a single past run."""
    run = analysis_service.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.delete("/history/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_run(run_id: int, db: Session = Depends(get_db)):
    if not analysis_service.delete_run(db, run_id):
        raise HTTPException(status_code=404, detail="Run not found")
