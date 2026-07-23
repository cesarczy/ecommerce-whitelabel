import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

import { ApiService } from '@core/services/api.service';
import { BannerResponse } from '@core/models/api.models';

@Component({
  standalone: true,
  imports: [RouterLink, MatButtonModule, MatCardModule],
  template: `
    @if (banners().length) {
      <div class="grid gap-4 mb-6">
        @for (banner of banners(); track banner.id) {
          <mat-card class="overflow-hidden">
            @if (banner.link_url) {
              <a [href]="banner.link_url" target="_blank" rel="noopener">
                <img [src]="banner.image_url" [alt]="banner.title" class="w-full max-h-64 object-cover" />
              </a>
            } @else {
              <img [src]="banner.image_url" [alt]="banner.title" class="w-full max-h-64 object-cover" />
            }
            <div class="p-3"><strong>{{ banner.title }}</strong></div>
          </mat-card>
        }
      </div>
    }
    <mat-card class="p-8 text-center bg-gradient-to-br from-indigo-50 to-white">
      <h1 class="text-3xl font-semibold mb-3">E-commerce Whitelabel</h1>
      <p class="text-gray-600 mb-6">Plataforma modular com catálogo, carrinho, checkout e painel admin.</p>
      <div class="flex gap-3 justify-center">
        <a mat-raised-button color="primary" routerLink="/products">Ver produtos</a>
        <a mat-stroked-button routerLink="/register">Criar conta</a>
      </div>
    </mat-card>
  `,
})
export class HomeComponent implements OnInit {
  private readonly api = inject(ApiService);
  banners = signal<BannerResponse[]>([]);

  ngOnInit(): void {
    this.api.listBanners().subscribe({ next: (items) => this.banners.set(items) });
  }
}
