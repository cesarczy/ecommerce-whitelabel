import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { Store } from '@ngxs/store';

import { ApiService } from '@core/services/api.service';
import { CartState } from '@core/state/cart.state';

@Component({
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
  ],
  template: `
    <h2 class="text-2xl font-medium mb-4">Checkout</h2>
    <mat-card class="p-4 max-w-lg">
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>Rua</mat-label><input matInput formControlName="street" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Número</mat-label><input matInput formControlName="number" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Bairro</mat-label><input matInput formControlName="neighborhood" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Cidade</mat-label><input matInput formControlName="city" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>UF</mat-label><input matInput formControlName="state" maxlength="2" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>CEP</mat-label><input matInput formControlName="cep" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Cupom (opcional)</mat-label><input matInput formControlName="coupon_code" /></mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Pagamento</mat-label>
          <mat-select formControlName="payment_method">
            <mat-option value="pix">PIX</mat-option>
            <mat-option value="credit_card">Cartão</mat-option>
            <mat-option value="boleto">Boleto</mat-option>
          </mat-select>
        </mat-form-field>
        @if (message) {
          <p class="text-sm text-green-700">{{ message }}</p>
        }
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Confirmar pedido</button>
      </form>
    </mat-card>
  `,
})
export class CheckoutComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ApiService);
  private readonly store = inject(Store);
  private readonly router = inject(Router);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({
    street: ['', Validators.required],
    number: ['', Validators.required],
    neighborhood: ['', Validators.required],
    city: ['', Validators.required],
    state: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(2)]],
    cep: ['', Validators.required],
    coupon_code: [''],
    payment_method: ['pix', Validators.required],
  });

  submit(): void {
    const cart = this.store.selectSnapshot(CartState.cart);
    if (!cart || this.form.invalid) return;
    this.loading = true;
    const { coupon_code, payment_method, ...address } = this.form.getRawValue();
    this.api.checkout({
      cart_id: cart.id,
      shipping_address: address,
      shipping_cost: '15.00',
      coupon_code: coupon_code || undefined,
    }).subscribe({
      next: (order) => {
        this.api.createPayment({ order_id: order.id, method: payment_method, provider: 'mock' }).subscribe({
          next: (payment) => {
            this.message = `Pedido ${order.order_number} — pagamento ${payment.status}`;
            this.router.navigateByUrl('/orders');
          },
          error: () => (this.loading = false),
        });
      },
      error: () => (this.loading = false),
    });
  }
}
