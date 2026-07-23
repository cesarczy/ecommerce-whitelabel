import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';

import { ApiService } from '@core/services/api.service';
import { ProductResponse } from '@core/models/api.models';

@Component({
  standalone: true,
  imports: [RouterLink, MatCardModule, MatButtonModule],
  template: `
    <h2 class="text-2xl font-medium mb-4">Favoritos</h2>
    <div class="grid gap-3 max-w-2xl">
      @for (product of favorites(); track product.id) {
        <mat-card class="p-4 flex justify-between items-center">
          <a [routerLink]="['/products', product.slug]" class="font-medium">{{ product.name }}</a>
          <button mat-stroked-button (click)="remove(product.id)">Remover</button>
        </mat-card>
      }
    </div>
  `,
})
export class FavoritesComponent implements OnInit {
  private readonly api = inject(ApiService);
  favorites = signal<ProductResponse[]>([]);

  ngOnInit(): void {
    this.api.listFavorites().subscribe({ next: (items) => this.favorites.set(items) });
  }

  remove(productId: string): void {
    this.api.removeFavorite(productId).subscribe({
      next: () => this.favorites.update((items) => items.filter((p) => p.id !== productId)),
    });
  }
}
