import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AsyncPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { Store } from '@ngxs/store';

import { CartState } from '@core/state/cart.state';

@Component({
  standalone: true,
  imports: [RouterLink, AsyncPipe, MatCardModule, MatButtonModule],
  template: `
    <h2 class="text-2xl font-medium mb-4">Carrinho</h2>
    @if (cart$ | async; as cart) {
      @if (cart.items.length === 0) {
        <p class="text-gray-500">Seu carrinho está vazio.</p>
      } @else {
        <mat-card class="p-4 mb-4">
          @for (item of cart.items; track item.id) {
            <div class="flex justify-between py-2 border-b last:border-0">
              <span>{{ item.product_name }} x{{ item.quantity }}</span>
              <span>R$ {{ item.line_total }}</span>
            </div>
          }
          <div class="flex justify-between font-semibold mt-4">
            <span>Subtotal</span>
            <span>R$ {{ cart.subtotal }}</span>
          </div>
        </mat-card>
        <a mat-raised-button color="primary" routerLink="/checkout">Finalizar compra</a>
      }
    } @else {
      <p class="text-gray-500">Seu carrinho está vazio.</p>
    }
  `,
})
export class CartComponent {
  private readonly store = inject(Store);
  readonly cart$ = this.store.select(CartState.cart);
}
