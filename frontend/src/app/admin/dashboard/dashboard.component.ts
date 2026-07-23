import { Component, inject, OnInit, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

import { ApiService } from '@core/services/api.service';
import { AnalyticsResponse } from '@core/models/api.models';

@Component({
  standalone: true,
  imports: [MatCardModule],
  template: `
    <h2 class="text-xl font-medium mb-4">Dashboard</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      @for (item of stats(); track item.label) {
        <mat-card class="p-4 text-center">
          <p class="text-sm text-gray-500">{{ item.label }}</p>
          <p class="text-2xl font-semibold">{{ item.value }}</p>
        </mat-card>
      }
    </div>
    @if (analytics()) {
      <h3 class="text-lg font-medium mb-3">Analytics</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <mat-card class="p-4 text-center"><p class="text-sm text-gray-500">Conversão</p><p class="text-xl">{{ analytics()?.conversion_rate }}%</p></mat-card>
        <mat-card class="p-4 text-center"><p class="text-sm text-gray-500">Carrinhos</p><p class="text-xl">{{ analytics()?.carts_count }}</p></mat-card>
        <mat-card class="p-4 text-center"><p class="text-sm text-gray-500">Favoritos</p><p class="text-xl">{{ analytics()?.favorites_count }}</p></mat-card>
        <mat-card class="p-4 text-center"><p class="text-sm text-gray-500">Reviews</p><p class="text-xl">{{ analytics()?.reviews_count }}</p></mat-card>
      </div>
    }
  `,
})
export class DashboardComponent implements OnInit {
  private readonly api = inject(ApiService);
  stats = signal<{ label: string; value: string | number }[]>([]);
  analytics = signal<AnalyticsResponse | null>(null);

  ngOnInit(): void {
    this.api.adminDashboard().subscribe({
      next: (data) => {
        this.stats.set([
          { label: 'Vendas', value: String(data['total_sales'] ?? '0') },
          { label: 'Pedidos', value: Number(data['orders_count'] ?? 0) },
          { label: 'Estoque baixo', value: Number(data['low_stock_count'] ?? 0) },
          { label: 'Clientes', value: Number(data['customers_count'] ?? 0) },
        ]);
      },
    });
    this.api.adminAnalytics().subscribe({ next: (data) => this.analytics.set(data) });
  }
}
