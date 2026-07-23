import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';

@Component({
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MatButtonModule],
  template: `
    <div class="mb-6">
      <h1 class="text-2xl font-medium mb-3">Painel Admin</h1>
      <nav class="flex flex-wrap gap-2">
        <a mat-stroked-button routerLink="/admin" routerLinkActive="mat-primary" [routerLinkActiveOptions]="{ exact: true }">
          Dashboard
        </a>
        <a mat-stroked-button routerLink="/admin/products" routerLinkActive="mat-primary">Produtos</a>
        <a mat-stroked-button routerLink="/admin/coupons" routerLinkActive="mat-primary">Cupons</a>
        <a mat-stroked-button routerLink="/admin/banners" routerLinkActive="mat-primary">Banners</a>
        <a mat-stroked-button routerLink="/admin/store" routerLinkActive="mat-primary">Loja</a>
      </nav>
    </div>
    <router-outlet />
  `,
})
export class AdminLayoutComponent {}
