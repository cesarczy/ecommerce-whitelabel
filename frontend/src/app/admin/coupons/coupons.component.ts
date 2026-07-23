import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';

import { ApiService } from '@core/services/api.service';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatSelectModule],
  template: `
    <h2 class="text-2xl font-medium mb-4">Cupons</h2>
    <mat-card class="p-4 max-w-lg">
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>Código</mat-label><input matInput formControlName="code" /></mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Tipo</mat-label>
          <mat-select formControlName="discount_type">
            <mat-option value="percent">Percentual</mat-option>
            <mat-option value="fixed">Fixo</mat-option>
          </mat-select>
        </mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Valor</mat-label><input matInput type="number" formControlName="discount_value" /></mat-form-field>
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Criar cupom</button>
      </form>
      @if (message) {
        <p class="mt-3 text-green-700">{{ message }}</p>
      }
    </mat-card>
  `,
})
export class CouponsComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({
    code: ['', Validators.required],
    discount_type: ['percent' as 'percent' | 'fixed', Validators.required],
    discount_value: [10, [Validators.required, Validators.min(1)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.createCoupon(this.form.getRawValue()).subscribe({
      next: (coupon) => {
        this.message = `Cupom ${coupon.code} criado`;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
