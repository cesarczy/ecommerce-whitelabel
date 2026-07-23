import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { Store } from '@ngxs/store';

import { Login } from '@core/state/auth.state';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <mat-card class="max-w-md mx-auto p-6">
      <h2 class="text-xl font-medium mb-4">Entrar</h2>
      <form [formGroup]="form" (ngSubmit)="submit()" class="flex flex-col gap-3">
        <mat-form-field appearance="outline">
          <mat-label>E-mail</mat-label>
          <input matInput type="email" formControlName="email" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Senha</mat-label>
          <input matInput type="password" formControlName="password" />
        </mat-form-field>
        @if (error) {
          <p class="text-red-600 text-sm">{{ error }}</p>
        }
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Entrar</button>
      </form>
      <p class="mt-4 text-sm">Não tem conta? <a routerLink="/register" class="text-indigo-600">Cadastre-se</a></p>
    </mat-card>
  `,
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly store = inject(Store);
  private readonly router = inject(Router);

  loading = false;
  error = '';
  form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    const { email, password } = this.form.getRawValue();
    this.store.dispatch(new Login(email, password)).subscribe({
      next: () => this.router.navigateByUrl('/products'),
      error: () => {
        this.error = 'Credenciais inválidas';
        this.loading = false;
      },
    });
  }
}
