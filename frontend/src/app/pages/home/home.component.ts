import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

@Component({
  standalone: true,
  imports: [RouterLink, MatButtonModule, MatCardModule],
  template: `
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
export class HomeComponent {}
