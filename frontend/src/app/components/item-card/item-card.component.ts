import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Item } from '../../models/item.model';

@Component({
  selector: 'app-item-card',
  imports: [RouterLink],
  templateUrl: './item-card.component.html',
  styleUrl: './item-card.component.css',
})
export class ItemCardComponent {
  item = input.required<Item>();
}
