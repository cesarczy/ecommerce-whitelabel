import { Component, inject, OnInit, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

import { ApiService } from '@core/services/api.service';
import { OrderResponse } from '@core/models/api.models';

@Component({
  standalone: true,
  imports: [MatCardModule, MatButtonModule, RouterLink],
  template: `
    <h2 class="text-2xl font-medium mb-4">Meus pedidos</h2>
    @if (orders().length === 0) {
      <p class="text-gray-600">Nenhum pedido encontrado.</p>
    }
    <div class="grid gap-3 max-w-2xl">
      @for (order of orders(); track order.id) {
        <mat-card class="p-4">
          <p><strong>#{{ order.order_number }}</strong> — {{ order.status }}</p>
          <p class="text-sm text-gray-600">Total: R$ {{ order.total }}</p>
        </mat-card>
      }
    </div>
    <a mat-button routerLink="/profile" class="mt-4 inline-block">Voltar ao perfil</a>
  `,
})
export class OrdersComponent implements OnInit {
  private readonly api = inject(ApiService);
  orders = signal<OrderResponse[]>([]);

  ngOnInit(): void {
    this.api.listOrders().subscribe({ next: (data) => this.orders.set(data) });
  }
}
