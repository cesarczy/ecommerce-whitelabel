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
      <h2 class="text-xl font-medium mb-4">Nova senha</h2>
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>Token</mat-label><input matInput formControlName="token" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Nova senha</mat-label><input matInput type="password" formControlName="new_password" /></mat-form-field>
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Redefinir</button>
      </form>
      @if (message) { <p class="mt-3 text-green-700 text-sm">{{ message }}</p> }
    </mat-card>
  `,
})
export class ResetPasswordComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  private readonly router = inject(Router);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({
    token: ['', Validators.required],
    new_password: ['', [Validators.required, Validators.minLength(8)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.resetPassword(this.form.getRawValue()).subscribe({
      next: () => {
        this.message = 'Senha redefinida com sucesso';
        this.router.navigateByUrl('/login');
      },
      error: () => (this.loading = false),
    });
  }
}
