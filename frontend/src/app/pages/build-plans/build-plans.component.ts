import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { BuildPlanSummary } from '../../models/build-plan.model';

@Component({
  selector: 'app-build-plans',
  imports: [RouterLink, DatePipe],
  templateUrl: './build-plans.component.html',
  styleUrl: './build-plans.component.css',
})
export class BuildPlansComponent {
  private readonly api = inject(ApiService);

  plans = signal<BuildPlanSummary[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.getPlans().subscribe({
      next: (plans) => {
        this.plans.set(plans);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load plans.');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  onDelete(plan: BuildPlanSummary, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    if (!confirm(`Delete "${plan.name}"? This cannot be undone.`)) return;

    this.api.deletePlan(plan.plan_id).subscribe({
      next: () => this.load(),
      error: (err) => {
        this.error.set('Failed to delete plan.');
        console.error(err);
      },
    });
  }
}
