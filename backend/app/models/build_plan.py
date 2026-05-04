from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.database import Base


class BuildPlan(Base):
    __tablename__ = "build_plans"

    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)  # Will do this if I have time
    name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    targets = relationship(
        "BuildPlanTarget",
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class BuildPlanTarget(Base):
    __tablename__ = "build_plan_targets"

    plan_id = Column(
        Integer, ForeignKey("build_plans.plan_id", ondelete="CASCADE"), primary_key=True
    )
    target_item_id = Column(
        Integer, ForeignKey("items.item_id"), primary_key=True
    )

    plan = relationship("BuildPlan", back_populates="targets")
    item = relationship("Item")
