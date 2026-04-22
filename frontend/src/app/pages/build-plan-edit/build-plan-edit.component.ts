import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Item } from '../../models/item.model';

@Component({
  selector: 'app-build-plan-edit',
  imports: [FormsModule, RouterLink],
  templateUrl: './build-plan-edit.component.html',
  styleUrl: './build-plan-edit.component.css',
})
export class BuildPlanEditComponent {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  // Form fields
  name = signal('');
  notes = signal('');
  targets = signal<Item[]>([]);

  // Item search state
  searchText = signal('');
  searchResults = signal<Item[]>([]);
  searchLoading = signal(false);

  // Page state
  planId = signal<number | null>(null);
  loading = signal(false);
  saving = signal(false);
  error = signal<string | null>(null);

  // Computed: is this an edit page or a create page?
  isEdit = computed(() => this.planId() !== null);

  constructor() {
    this.route.paramMap.subscribe((params) => {
      const id = params.get('id');
      if (id) {
        const parsed = Number(id);
        if (!isNaN(parsed)) {
          this.planId.set(parsed);
          this.loadPlan(parsed);
        }
      }
    });
  }

  private loadPlan(id: number): void {
    this.loading.set(true);
    this.api.getPlan(id).subscribe({
      next: (plan) => {
        this.name.set(plan.name);
        this.notes.set(plan.notes ?? '');
        this.targets.set(plan.targets);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Could not load plan.');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  onSearch(): void {
    const q = this.searchText().trim();
    if (!q) {
      this.searchResults.set([]);
      return;
    }
    this.searchLoading.set(true);
    this.api.getItems({ search: q }).subscribe({
      next: (items) => {
        this.searchResults.set(items.slice(0, 20));
        this.searchLoading.set(false);
      },
      error: () => {
        this.searchResults.set([]);
        this.searchLoading.set(false);
      },
    });
  }

  addTarget(item: Item): void {
    if (this.targets().some((t) => t.item_id === item.item_id)) return;
    this.targets.update((arr) => [...arr, item]);
  }

  removeTarget(itemId: number): void {
    this.targets.update((arr) => arr.filter((t) => t.item_id !== itemId));
  }

  canSave(): boolean {
    return (
      this.name().trim().length > 0 &&
      this.targets().length > 0 &&
      !this.saving()
    );
  }

  save(): void {
    if (!this.canSave()) return;
    this.saving.set(true);
    this.error.set(null);

    const payload = {
      name: this.name().trim(),
      notes: this.notes().trim() || null,
      target_item_ids: this.targets().map((t) => t.item_id),
    };

    const id = this.planId();
    const request$ = id
      ? this.api.updatePlan(id, payload)
      : this.api.createPlan(payload);

    request$.subscribe({
      next: () => {
        this.router.navigate(['/plans']);
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? 'Failed to save plan.');
        this.saving.set(false);
        console.error(err);
      },
    });
  }
}
