import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { ItemDetail } from '../../models/item.model';

@Component({
  selector: 'app-item-detail',
  imports: [RouterLink],
  templateUrl: './item-detail.component.html',
  styleUrl: './item-detail.component.css',
})
export class ItemDetailComponent {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);

  item = signal<ItemDetail | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);

  constructor() {
    this.route.paramMap.subscribe((params) => {
      const id = Number(params.get('id'));
      if (!isNaN(id)) {
        this.loadItem(id);
      }
    });
  }

  private loadItem(id: number): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.getItem(id).subscribe({
      next: (detail) => {
        this.item.set(detail);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Could not load item.');
        this.loading.set(false);
        console.error(err);
      },
    });
  }
}
