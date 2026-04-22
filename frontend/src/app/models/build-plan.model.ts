import { Item } from './item.model';

export interface BuildPlanSummary {
  plan_id: number;
  name: string;
  notes: string | null;
  target_count: number;
  created_at: string;
}

export interface BuildPlan {
  plan_id: number;
  name: string;
  notes: string | null;
  created_at: string;
  targets: Item[];
}

export interface BuildPlanCreate {
  name: string;
  notes?: string | null;
  target_item_ids: number[];
}

export interface BuildPlanUpdate {
  name?: string;
  notes?: string | null;
  target_item_ids?: number[];
}
