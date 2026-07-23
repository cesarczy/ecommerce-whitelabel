import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
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
      <h2 class="text-xl font-medium mb-4">Cadastro</h2>
      <form [formGroup]="form" (ngSubmit)="submit()" class="flex flex-col gap-3">
        <mat-form-field appearance="outline">
          <mat-label>Nome completo</mat-label>
          <input matInput formControlName="full_name" />
        </mat-form-field>
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
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Cadastrar</button>
      </form>
      <p class="mt-4 text-sm"><a routerLink="/login" class="text-indigo-600">Já tenho conta</a></p>
    </mat-card>
  `,
})
export class RegisterComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  loading = false;
  error = '';
  form = this.fb.nonNullable.group({
    full_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.register(this.form.getRawValue()).subscribe({
      next: () => this.router.navigateByUrl('/login'),
      error: () => {
        this.error = 'Não foi possível cadastrar';
        this.loading = false;
      },
    });
  }
}
