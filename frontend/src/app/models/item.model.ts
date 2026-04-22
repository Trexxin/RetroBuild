export interface Item {
  item_id: number;
  name: string;
  total_cost: number;
  purchasable: boolean;
  icon_url: string | null;
}

export interface RecipeEntry {
  item_id: number;
  name: string;
  total_cost: number;
  icon_url: string | null;
  qty: number;
}

export interface ItemDetail extends Item {
  description: string | null;
  version_tag: string;
  components: RecipeEntry[];
  builds_into: RecipeEntry[];
}
