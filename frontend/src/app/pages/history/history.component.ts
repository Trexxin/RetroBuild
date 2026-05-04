import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import {
  AnalysisRun,
  AnalysisRunSummary,
} from '../../models/analysis.model';
import { BuildPlanSummary } from '../../models/build-plan.model';

@Component({
  selector: 'app-history',
  imports: [FormsModule, DatePipe, RouterLink],
  templateUrl: './history.component.html',
  styleUrl: './history.component.css',
})
export class HistoryComponent {
  private readonly api = inject(ApiService);

  // Top-level state
  runs = signal<AnalysisRunSummary[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  // Filter
  plans = signal<BuildPlanSummary[]>([]);
  selectedPlanFilter = signal<number | null>(null);

  // Expanded detail
  expandedRunId = signal<number | null>(null);
  expandedDetail = signal<AnalysisRun | null>(null);
  loadingDetail = signal(false);

  constructor() {
    this.loadRuns();
    this.loadPlans();
  }

  loadRuns(): void {
    this.loading.set(true);
    this.error.set(null);
    const filter = this.selectedPlanFilter();
    this.api
      .getAnalysisHistory(filter ?? undefined)
      .subscribe({
        next: (runs) => {
          this.runs.set(runs);
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set('Failed to load history.');
          this.loading.set(false);
          console.error(err);
        },
      });
  }

  private loadPlans(): void {
    this.api.getPlans().subscribe({
      next: (plans) => this.plans.set(plans),
      error: (err) => console.error('Could not load plans for filter', err),
    });
  }

  onFilterChange(value: string): void {
    // <option [ngValue]="null"> sends the literal string "null" through (string)
    const parsed = value === 'null' || value === '' ? null : Number(value);
    this.selectedPlanFilter.set(parsed);
    // Collapse any expanded detail since the list is changing
    this.expandedRunId.set(null);
    this.expandedDetail.set(null);
    this.loadRuns();
  }

  toggleExpand(runId: number): void {
    if (this.expandedRunId() === runId) {
      // Collapse
      this.expandedRunId.set(null);
      this.expandedDetail.set(null);
      return;
    }
    this.expandedRunId.set(runId);
    this.expandedDetail.set(null);
    this.loadingDetail.set(true);
    this.api.getAnalysisRun(runId).subscribe({
      next: (run) => {
        this.expandedDetail.set(run);
        this.loadingDetail.set(false);
      },
      error: (err) => {
        this.loadingDetail.set(false);
        console.error(err);
      },
    });
  }

  onDelete(run: AnalysisRunSummary, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    const confirmation = `Delete this analysis run from ${new Date(
      run.created_at
    ).toLocaleString()}?`;
    if (!confirm(confirmation)) return;

    this.api.deleteAnalysisRun(run.run_id).subscribe({
      next: () => {
        if (this.expandedRunId() === run.run_id) {
          this.expandedRunId.set(null);
          this.expandedDetail.set(null);
        }
        this.loadRuns();
      },
      error: (err) => {
        this.error.set('Failed to delete run.');
        console.error(err);
      },
    });
  }
}
