import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { BuildPlanSummary } from '../../models/build-plan.model';
import { Item } from '../../models/item.model';
import { AnalysisRun } from '../../models/analysis.model';

const SLOT_COUNT = 6;

@Component({
  selector: 'app-run-analysis',
  imports: [FormsModule, RouterLink],
  templateUrl: './run-analysis.component.html',
  styleUrl: './run-analysis.component.css',
})
export class RunAnalysisComponent {
  private readonly api = inject(ApiService);

  // Plan selection
  plans = signal<BuildPlanSummary[]>([]);
  selectedPlanId = signal<number | null>(null);

  // Inputs
  currentGold = signal(0);
  inventory = signal<(Item | null)[]>(Array(SLOT_COUNT).fill(null));

  // Item picker (modal-style)
  pickerOpenForSlot = signal<number | null>(null);
  pickerSearch = signal('');
  pickerResults = signal<Item[]>([]);

  // Analysis result
  result = signal<AnalysisRun | null>(null);
  running = signal(false);
  error = signal<string | null>(null);

  // Derived
  occupiedSlots = computed(
    () => this.inventory().filter((i) => i !== null).length
  );

  canRun = computed(
    () =>
      this.selectedPlanId() !== null &&
      this.currentGold() >= 0 &&
      !this.running()
  );

  constructor() {
    this.api.getPlans().subscribe({
      next: (plans) => {
        this.plans.set(plans);
        if (plans.length > 0) this.selectedPlanId.set(plans[0].plan_id);
      },
      error: (err) => {
        this.error.set('Could not load plans.');
        console.error(err);
      },
    });
  }

  //  inventory picker

  openPicker(slotIndex: number): void {
    this.pickerOpenForSlot.set(slotIndex);
    this.pickerSearch.set('');
    this.pickerResults.set([]);
  }

  closePicker(): void {
    this.pickerOpenForSlot.set(null);
  }

  onPickerSearch(): void {
    const q = this.pickerSearch().trim();
    if (!q) {
      this.pickerResults.set([]);
      return;
    }
    this.api.getItems({ search: q }).subscribe({
      next: (items) => this.pickerResults.set(items.slice(0, 30)),
      error: () => this.pickerResults.set([]),
    });
  }

  pickItem(item: Item): void {
    const slot = this.pickerOpenForSlot();
    if (slot === null) return;
    this.inventory.update((arr) => {
      const next = [...arr];
      next[slot] = item;
      return next;
    });
    this.closePicker();
  }

  clearSlot(slotIndex: number, event: Event): void {
    event.stopPropagation();
    this.inventory.update((arr) => {
      const next = [...arr];
      next[slotIndex] = null;
      return next;
    });
  }

  //  run

  runAnalysis(): void {
    if (!this.canRun()) return;
    this.running.set(true);
    this.error.set(null);

    const inventory_item_ids = this.inventory()
      .filter((i): i is Item => i !== null)
      .map((i) => i.item_id);

    this.api
      .runAnalysis({
        plan_id: this.selectedPlanId()!,
        current_gold: this.currentGold(),
        inventory_item_ids,
      })
      .subscribe({
        next: (run) => {
          this.result.set(run);
          this.running.set(false);
        },
        error: (err) => {
          this.error.set(err?.error?.detail ?? 'Failed to run analysis.');
          this.running.set(false);
          console.error(err);
        },
      });
  }
}
