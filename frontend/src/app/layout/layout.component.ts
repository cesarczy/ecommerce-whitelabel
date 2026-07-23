import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AsyncPipe } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatBadgeModule } from '@angular/material/badge';
import { Store } from '@ngxs/store';

import { AuthState, Logout } from '@core/state/auth.state';
import { CartState } from '@core/state/cart.state';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, AsyncPipe, MatToolbarModule, MatButtonModule, MatIconModule, MatBadgeModule],
  template: `
    <mat-toolbar color="primary" class="shadow-md">
      <a routerLink="/" class="font-medium text-white no-underline mr-6">Whitelabel Store</a>
      <a mat-button routerLink="/products" routerLinkActive="opacity-80">Produtos</a>
      <a mat-button routerLink="/cart" routerLinkActive="opacity-80">
        Carrinho
        @if ((itemCount$ | async); as count) {
          @if (count > 0) {
            <span class="ml-1">({{ count }})</span>
          }
        }
      </a>
      <span class="flex-1"></span>
      @if (isAuth$ | async) {
        <a mat-button routerLink="/profile">Perfil</a>
        <a mat-button routerLink="/admin">Admin</a>
        <button mat-button (click)="logout()">Sair</button>
      } @else {
        <a mat-button routerLink="/login">Entrar</a>
        <a mat-button routerLink="/register">Cadastrar</a>
      }
    </mat-toolbar>
    <main class="max-w-6xl mx-auto p-6">
      <ng-content />
    </main>
  `,
})
export class LayoutComponent {
  private readonly store = inject(Store);
  readonly isAuth$ = this.store.select(AuthState.isAuthenticated);
  readonly itemCount$ = this.store.select(CartState.itemCount);

  logout(): void {
    this.store.dispatch(new Logout());
  }
}
