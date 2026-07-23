import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { Store } from '@ngxs/store';

import { ApiService } from '@core/services/api.service';
import { ProductResponse } from '@core/models/api.models';
import { CartState, SetCart } from '@core/state/cart.state';
import { AuthState } from '@core/state/auth.state';

@Component({
  standalone: true,
  imports: [RouterLink, MatCardModule, MatButtonModule],
  template: `
    @if (product(); as p) {
      <mat-card class="p-6 max-w-3xl">
        <h2 class="text-2xl font-medium mb-2">{{ p.name }}</h2>
        <p class="text-gray-600 mb-4">{{ p.description }}</p>
        <p class="text-xl font-semibold mb-4">R$ {{ p.price }}</p>
        <div class="flex gap-2 flex-wrap">
          <button mat-raised-button color="primary" (click)="addToCart(p)">Adicionar ao carrinho</button>
          @if (isLoggedIn()) {
            <button mat-stroked-button (click)="toggleFavorite(p)">{{ favorited() ? 'Remover favorito' : 'Favoritar' }}</button>
          }
        </div>
      </mat-card>
      @if (related().length) {
        <h3 class="text-lg font-medium mt-8 mb-3">Produtos relacionados</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          @for (item of related(); track item.id) {
            <mat-card class="p-4">
              <a [routerLink]="['/products', item.slug]" class="font-medium">{{ item.name }}</a>
              <p class="text-sm text-gray-600">R$ {{ item.price }}</p>
            </mat-card>
          }
        </div>
      }
    }
  `,
})
export class ProductDetailComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly store = inject(Store);

  product = signal<ProductResponse | null>(null);
  related = signal<ProductResponse[]>([]);
  favorited = signal(false);
  isLoggedIn = signal(false);

  ngOnInit(): void {
    this.isLoggedIn.set(!!this.store.selectSnapshot(AuthState.accessToken));
    const slug = this.route.snapshot.paramMap.get('slug')!;
    this.api.getProductBySlug(slug).subscribe({
      next: (p) => {
        this.product.set(p);
        this.api.getRelatedProducts(p.id).subscribe({ next: (items) => this.related.set(items) });
        if (this.isLoggedIn()) {
          this.api.listFavorites().subscribe({
            next: (favs) => this.favorited.set(favs.some((f) => f.id === p.id)),
          });
        }
      },
    });
  }

  addToCart(product: ProductResponse): void {
    const sessionId = this.store.selectSnapshot(CartState.sessionId);
    this.api.addToCart({ product_id: product.id, sku: product.sku, quantity: 1, session_id: sessionId }).subscribe({
      next: (cart) => this.store.dispatch(new SetCart(cart)),
    });
  }

  toggleFavorite(product: ProductResponse): void {
    if (this.favorited()) {
      this.api.removeFavorite(product.id).subscribe({ next: () => this.favorited.set(false) });
    } else {
      this.api.addFavorite(product.id).subscribe({ next: () => this.favorited.set(true) });
    }
  }
}
