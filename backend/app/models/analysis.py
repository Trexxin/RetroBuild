from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    run_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(
        Integer, ForeignKey("build_plans.plan_id"), nullable=False
    )
    user_id = Column(Integer, nullable=True)  # Reserved for auth
    current_gold = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("current_gold >= 0", name="ck_analysis_gold_nonneg"),
    )

    plan = relationship("BuildPlan")
    inventory = relationship(
        "RunInventoryItem",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="RunInventoryItem.slot_index",
    )
    path_steps = relationship(
        "RunPathStep",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="RunPathStep.step_num",
    )


class RunInventoryItem(Base):
    """One row per occupied inventory slot at the time of the run."""
    __tablename__ = "run_inventory_items"

    run_id = Column(
        Integer,
        ForeignKey("analysis_runs.run_id", ondelete="CASCADE"),
        primary_key=True,
    )
    slot_index = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "slot_index >= 0 AND slot_index <= 5",
            name="ck_inventory_slot_range",
        ),
    )

    run = relationship("AnalysisRun", back_populates="inventory")
    item = relationship("Item")


class RunPathStep(Base):
    """One row per step in the recommended purchase sequence."""
    __tablename__ = "run_path_steps"

    run_id = Column(
        Integer,
        ForeignKey("analysis_runs.run_id", ondelete="CASCADE"),
        primary_key=True,
    )
    step_num = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    step_cost = Column(Integer, nullable=False)

    run = relationship("AnalysisRun", back_populates="path_steps")
    item = relationship("Item")
