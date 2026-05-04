"""
Graph service: shortest-path analysis on the LoL item upgrade graph.

Ports my core algorithm from Johnson's_Algorithm.ipynb:
- Each item is a node.
- Each recipe relationship (component -> upgrade) is a directed edge whose
  weight is the GOLD COST of that upgrade step (= upgrade.total_cost - component.total_cost).
- Shortest paths in this graph correspond to the cheapest sequence of
  purchases to reach a target item from a starting state.

The graph is built once at FastAPI startup and held in memory.
"""

from typing import Iterable
import networkx as nx
from sqlalchemy.orm import Session
from app.models.item import Item, ItemRecipe

# Sentinel node added to the graph to represent "no inventory yet".
# It has zero-weight edges to every basic item (items with no components),
# so a search from this node naturally finds the cheapest target from scratch.
VIRTUAL_SOURCE = -1


class GraphService:
    def __init__(self) -> None:
        self._graph: nx.DiGraph | None = None
        self._item_names: dict[int, str] = {}
        self._item_total_cost: dict[int, int] = {}

    # Lifecycle

    def build_graph_from_db(self, db: Session) -> None:
        """Load items + recipes from MySQL and build the NetworkX graph."""
        graph = nx.DiGraph()

        items = db.query(Item).all()
        recipes = db.query(ItemRecipe).all()

        for item in items:
            graph.add_node(item.item_id)
            self._item_names[item.item_id] = item.name
            self._item_total_cost[item.item_id] = item.total_cost

        # Real edges: component -> upgrade, weighted by the gold delta.
        for r in recipes:
            parent_cost = self._item_total_cost.get(r.parent_item_id)
            comp_cost = self._item_total_cost.get(r.component_item_id)
            if parent_cost is None or comp_cost is None:
                continue
            upgrade_cost = parent_cost - comp_cost
            graph.add_edge(
                r.component_item_id,
                r.parent_item_id,
                weight=max(upgrade_cost, 0),
            )

        # Virtual source: zero-cost edge to every "root" basic item.
        # An item is "basic" if nothing builds INTO it (in_degree == 0).
        graph.add_node(VIRTUAL_SOURCE)
        for node in list(graph.nodes()):
            if node == VIRTUAL_SOURCE:
                continue
            if graph.in_degree(node) == 0:
                graph.add_edge(
                    VIRTUAL_SOURCE,
                    node,
                    weight=self._item_total_cost.get(node, 0),
                )

        self._graph = graph

    @property
    def is_ready(self) -> bool:
        return self._graph is not None

    # The core algorithm

    def find_optimal_path(
        self,
        inventory_item_ids: Iterable[int],
        target_item_ids: Iterable[int],
        current_gold: int,
    ) -> dict:
        """
        Find the cheapest target item reachable from any inventory item.

        Returns a dict shaped like:
            {
              "target_item_id": int | None,
              "path": list[(item_id, step_cost)],
              "total_path_cost": int,
              "message": str | None,
            }
        - If the user already owns a target, returns that as a zero-cost result.
        - If inventory is empty, treats it as starting from the virtual source.
        - If no inventory item can reach any target, returns target_item_id=None
          with an explanatory message.
        """
        if self._graph is None:
            raise RuntimeError("Graph not initialized")

        targets = list(target_item_ids)
        inventory = list(inventory_item_ids)

        # Owned-target shortcut: if the user already has any target, no work to do.
        owned_targets = set(inventory) & set(targets)
        if owned_targets:
            tgt = next(iter(owned_targets))
            return {
                "target_item_id": tgt,
                "path": [(tgt, 0)],
                "total_path_cost": 0,
                "message": f"You already own {self._item_names.get(tgt, tgt)}.",
            }

        # If empty inventory, search from the virtual source.
        sources = inventory if inventory else [VIRTUAL_SOURCE]

        best_total = None
        best_pair = None  # (source_id, target_id)

        for source in sources:
            if source not in self._graph:
                continue
            for target in targets:
                if target not in self._graph:
                    continue
                if source == target:
                    continue
                if not nx.has_path(self._graph, source, target):
                    continue
                cost = nx.shortest_path_length(
                    self._graph, source=source, target=target, weight="weight"
                )
                if best_total is None or cost < best_total:
                    best_total = cost
                    best_pair = (source, target)

        if best_pair is None:
            return {
                "target_item_id": None,
                "path": [],
                "total_path_cost": 0,
                "message": (
                    "None of your inventory items can be upgraded into a plan target. "
                    "Consider selling something or starting a fresh build."
                ),
            }

        source, target = best_pair
        node_path = nx.shortest_path(
            self._graph, source=source, target=target, weight="weight"
        )

        # Convert node list to (item_id, step_cost) list.
        # Skip the virtual source if present.
        steps: list[tuple[int, int]] = []
        for i, node in enumerate(node_path):
            if node == VIRTUAL_SOURCE:
                continue
            if i == 0:
                # Starting inventory item — step_cost is 0 (already owned).
                steps.append((node, 0))
            else:
                prev = node_path[i - 1]
                edge_data = self._graph.get_edge_data(prev, node)
                step_cost = edge_data["weight"] if edge_data else 0
                steps.append((node, step_cost))

        # If the path started at the virtual source, the first real step has its
        # full total_cost as step_cost (the edge weight from source). Re-attribute it
        # so the "step" represents buying that item, not "owning" it.

        return {
            "target_item_id": target,
            "path": steps,
            "total_path_cost": best_total,
            "message": None,
        }

    # Helpers exposed to other layers

    def item_name(self, item_id: int) -> str | None:
        return self._item_names.get(item_id)


graph_service = GraphService()
