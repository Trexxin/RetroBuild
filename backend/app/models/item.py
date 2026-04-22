from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, autoincrement=False)  # Riot's ID
    name = Column(String(100), nullable=False)
    total_cost = Column(Integer, nullable=False, default=0)
    purchasable = Column(Boolean, nullable=False, default=True)
    version_tag = Column(String(20), nullable=False)
    icon_url = Column(String(255))
    description = Column(Text)

    # Relationships: what components build INTO this item
    components = relationship(
        "ItemRecipe",
        foreign_keys="ItemRecipe.parent_item_id",
        back_populates="parent",
    )
    # Relationships: what this item builds into
    builds_into = relationship(
        "ItemRecipe",
        foreign_keys="ItemRecipe.component_item_id",
        back_populates="component",
    )


class ItemRecipe(Base):
    __tablename__ = "item_recipe"

    parent_item_id = Column(
        Integer, ForeignKey("items.item_id"), primary_key=True
    )
    component_item_id = Column(
        Integer, ForeignKey("items.item_id"), primary_key=True
    )
    qty = Column(Integer, nullable=False, default=1)

    parent = relationship(
        "Item", foreign_keys=[parent_item_id], back_populates="components"
    )
    component = relationship(
        "Item", foreign_keys=[component_item_id], back_populates="builds_into"
    )
