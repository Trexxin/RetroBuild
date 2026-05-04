"""
Seed script: fetches item data from Riot's Data Dragon API and populates
the items and item_recipe tables.

Adapted from my Johnson's_Algorithm.ipynb — build_league_graph() function.

Usage:
    cd backend
    python -m app.seed.seed_items
"""

import requests
from collections import Counter
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models.item import Item, ItemRecipe
from app.config import settings


def fetch_ddragon_items(version: str) -> dict:
    """Fetch raw item data from Riot's Data Dragon CDN."""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["data"]


def seed_items(db: Session, version: str = None):
    """
    Fetch items from Data Dragon and insert into the database.

    This mirrors the notebook's filtering logic:
    - Only Summoner's Rift items (map 11)
    - Only purchasable items
    """
    version = version or settings.DDRAGON_VERSION
    print(f"Fetching item data for patch {version}...")
    raw_data = fetch_ddragon_items(version)

    # Track which item IDs we insert (for recipe validation)
    inserted_ids = set()
    items_to_add = []
    recipes_to_add = []

    # --- Pass 1: Insert items ---
    for item_id_str, attrs in raw_data.items():
        maps = attrs.get("maps", {})
        is_rift = maps.get("11", False)
        is_purchasable = attrs.get("gold", {}).get("purchasable", False)

        if not (is_rift and is_purchasable):
            continue

        item_id = int(item_id_str)
        icon_url = (
            f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item_id_str}.png"
        )

        item = Item(
            item_id=item_id,
            name=attrs["name"],
            total_cost=attrs["gold"]["total"],
            purchasable=True,
            version_tag=version,
            icon_url=icon_url,
            description=attrs.get("plaintext", ""),
        )
        items_to_add.append(item)
        inserted_ids.add(item_id)

    db.add_all(items_to_add)
    db.flush()  # Flush so FKs are valid for recipes
    print(f"Inserted {len(items_to_add)} items.")

    # --- Pass 2: Insert recipes ---
    for item_id_str, attrs in raw_data.items():
        item_id = int(item_id_str)
        if item_id not in inserted_ids:
            continue

        component_ids = attrs.get("from", [])
        if not component_ids:
            continue

        # Count duplicates: e.g., ["1036", "1036"] -> {1036: 2}
        component_counts = Counter(int(cid) for cid in component_ids)

        for comp_id, qty in component_counts.items():
            # Only add recipe if the component is also in our filtered set
            if comp_id in inserted_ids:
                recipe = ItemRecipe(
                    parent_item_id=item_id,
                    component_item_id=comp_id,
                    qty=qty,
                )
                recipes_to_add.append(recipe)

    db.add_all(recipes_to_add)
    db.commit()
    print(f"Inserted {len(recipes_to_add)} recipes.")
    print("Seeding complete!")


def main():
    """Entry point: create tables and run the seed."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # Clear existing data for a clean re-seed
        db.query(ItemRecipe).delete()
        db.query(Item).delete()
        db.commit()
        print("Cleared existing data.")

        seed_items(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
