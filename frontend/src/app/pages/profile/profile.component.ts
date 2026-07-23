import { Component, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
import { Store } from '@ngxs/store';

import { AuthState } from '@core/state/auth.state';

@Component({
  standalone: true,
  imports: [AsyncPipe, MatCardModule, MatButtonModule, RouterLink],
  template: `
    <h2 class="text-2xl font-medium mb-4">Meu perfil</h2>
    @if (user$ | async; as user) {
      <mat-card class="p-4 max-w-md">
        <p><strong>Nome:</strong> {{ user.full_name }}</p>
        <p><strong>E-mail:</strong> {{ user.email }}</p>
        <p><strong>Roles:</strong> {{ user.roles.join(', ') }}</p>
        <div class="flex gap-2 mt-4 flex-wrap">
          <a mat-stroked-button routerLink="/orders">Meus pedidos</a>
          <a mat-stroked-button routerLink="/favorites">Favoritos</a>
          <a mat-stroked-button routerLink="/mfa">MFA</a>
          @if (!(user.email_verified)) {
            <a mat-stroked-button routerLink="/verify-email">Confirmar e-mail</a>
          }
        </div>
      </mat-card>
    }
  `,
})
export class ProfileComponent {
  private readonly store = inject(Store);
  readonly user$ = this.store.select(AuthState.user);
}
