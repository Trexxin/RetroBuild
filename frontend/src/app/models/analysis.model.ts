import { Item } from './item.model';

export interface PathStep {
  step_num: number;
  item_id: number;
  item_name: string;
  icon_url: string | null;
  step_cost: number;
}

export interface AnalysisRun {
  run_id: number;
  plan_id: number;
  plan_name: string;
  current_gold: number;
  created_at: string;
  inventory: Item[];
  target_item: Item | null;
  path_steps: PathStep[];
  total_path_cost: number;
  gold_remaining: number;
  message: string | null;
}

export interface AnalysisRunSummary {
  run_id: number;
  plan_id: number;
  plan_name: string;
  current_gold: number;
  created_at: string;
  target_item_name: string | null;
  total_path_cost: number;
}

export interface AnalysisRunCreate {
  plan_id: number;
  current_gold: number;
  inventory_item_ids: number[];
}
