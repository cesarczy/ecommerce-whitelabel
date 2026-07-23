import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

import { ApiService } from '@core/services/api.service';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <mat-card class="max-w-md mx-auto p-6">
      <h2 class="text-xl font-medium mb-4">Confirmar e-mail</h2>
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>Token</mat-label><input matInput formControlName="token" /></mat-form-field>
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Confirmar</button>
      </form>
      @if (message) { <p class="mt-3 text-green-700 text-sm">{{ message }}</p> }
      <a routerLink="/profile" class="text-sm text-indigo-600 mt-4 inline-block">Voltar ao perfil</a>
    </mat-card>
  `,
})
export class VerifyEmailComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({ token: ['', Validators.required] });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.verifyEmail(this.form.controls.token.value).subscribe({
      next: () => {
        this.message = 'E-mail confirmado com sucesso';
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
