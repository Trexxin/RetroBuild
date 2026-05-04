import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Item, ItemDetail } from '../models/item.model';
import {
  BuildPlan,
  BuildPlanCreate,
  BuildPlanSummary,
  BuildPlanUpdate,
} from '../models/build-plan.model';
import {
  AnalysisRun,
  AnalysisRunCreate,
  AnalysisRunSummary,
} from '../models/analysis.model';

export interface ItemQuery {
  search?: string;
  min_cost?: number;
  max_cost?: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';
  private readonly http = inject(HttpClient);

  // Items

  getItems(query: ItemQuery = {}): Observable<Item[]> {
    let params = new HttpParams();
    if (query.search) params = params.set('search', query.search);
    if (query.min_cost !== undefined)
      params = params.set('min_cost', query.min_cost);
    if (query.max_cost !== undefined)
      params = params.set('max_cost', query.max_cost);

    return this.http.get<Item[]>(`${this.baseUrl}/items`, { params });
  }

  getItem(itemId: number): Observable<ItemDetail> {
    return this.http.get<ItemDetail>(`${this.baseUrl}/items/${itemId}`);
  }

  // Build Plans

  getPlans(): Observable<BuildPlanSummary[]> {
    return this.http.get<BuildPlanSummary[]>(`${this.baseUrl}/plans`);
  }

  getPlan(planId: number): Observable<BuildPlan> {
    return this.http.get<BuildPlan>(`${this.baseUrl}/plans/${planId}`);
  }

  createPlan(payload: BuildPlanCreate): Observable<BuildPlan> {
    return this.http.post<BuildPlan>(`${this.baseUrl}/plans`, payload);
  }

  updatePlan(planId: number, payload: BuildPlanUpdate): Observable<BuildPlan> {
    return this.http.put<BuildPlan>(
      `${this.baseUrl}/plans/${planId}`,
      payload
    );
  }

  deletePlan(planId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/plans/${planId}`);
  }

  // Analysis

  runAnalysis(payload: AnalysisRunCreate): Observable<AnalysisRun> {
    return this.http.post<AnalysisRun>(
      `${this.baseUrl}/analysis/run`,
      payload
    );
  }

  getAnalysisHistory(planId?: number): Observable<AnalysisRunSummary[]> {
    let params = new HttpParams();
    if (planId !== undefined) params = params.set('plan_id', planId);
    return this.http.get<AnalysisRunSummary[]>(
      `${this.baseUrl}/analysis/history`,
      { params }
    );
  }

  getAnalysisRun(runId: number): Observable<AnalysisRun> {
    return this.http.get<AnalysisRun>(
      `${this.baseUrl}/analysis/history/${runId}`
    );
  }

  deleteAnalysisRun(runId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/analysis/history/${runId}`);
  }
}
