import { Component, inject, OnInit, signal } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Store } from '@ngxs/store';

import { ApiService } from '@core/services/api.service';
import { ProductResponse } from '@core/models/api.models';
import { CartState, SetCart } from '@core/state/cart.state';

@Component({
  standalone: true,
  imports: [CurrencyPipe, MatCardModule, MatButtonModule, MatProgressSpinnerModule, RouterLink],
  template: `
    <h2 class="text-2xl font-medium mb-4">Catálogo</h2>
    @if (loading()) {
      <mat-spinner diameter="40" />
    } @else if (products().length === 0) {
      <p class="text-gray-500">Nenhum produto disponível.</p>
    } @else {
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        @for (product of products(); track product.id) {
          <mat-card class="p-4">
            <h3 class="font-medium">{{ product.name }}</h3>
            <p class="text-sm text-gray-600 line-clamp-2 mb-2">{{ product.description }}</p>
            <p class="text-lg font-semibold mb-3">R$ {{ product.price }}</p>
            <div class="flex gap-2">
              <a mat-stroked-button [routerLink]="['/products', product.slug]">Detalhes</a>
              <button mat-raised-button color="primary" (click)="addToCart(product)">Adicionar</button>
            </div>
          </mat-card>
        }
      </div>
    }
  `,
})
export class ProductsComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly store = inject(Store);

  products = signal<ProductResponse[]>([]);
  loading = signal(true);

  ngOnInit(): void {
    this.api.listProducts().subscribe({
      next: (items) => {
        this.products.set(items);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  addToCart(product: ProductResponse): void {
    const sessionId = this.store.selectSnapshot(CartState.sessionId);
    this.api.addToCart({ product_id: product.id, sku: product.sku, quantity: 1, session_id: sessionId }).subscribe({
      next: (cart) => this.store.dispatch(new SetCart(cart)),
    });
  }
}
