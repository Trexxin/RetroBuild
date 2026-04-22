import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Item } from '../../models/item.model';
import { ItemCardComponent } from '../../components/item-card/item-card.component';

@Component({
  selector: 'app-item-browser',
  imports: [FormsModule, ItemCardComponent],
  templateUrl: './item-browser.component.html',
  styleUrl: './item-browser.component.css',
})
export class ItemBrowserComponent {
  private readonly api = inject(ApiService);

  search = signal('');
  items = signal<Item[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.getItems({ search: this.search() || undefined }).subscribe({
      next: (items) => {
        this.items.set(items);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load items. Is the backend running?');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  onSearch(): void {
    this.load();
  }
}
