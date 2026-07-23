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
      <h2 class="text-xl font-medium mb-4">Esqueci minha senha</h2>
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>E-mail</mat-label><input matInput type="email" formControlName="email" /></mat-form-field>
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Enviar</button>
      </form>
      @if (message) { <p class="mt-3 text-green-700 text-sm">{{ message }}</p> }
      <a routerLink="/login" class="text-sm text-indigo-600 mt-4 inline-block">Voltar ao login</a>
    </mat-card>
  `,
})
export class ForgotPasswordComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({ email: ['', [Validators.required, Validators.email]] });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.forgotPassword(this.form.controls.email.value).subscribe({
      next: (res) => {
        this.message = res.message;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
