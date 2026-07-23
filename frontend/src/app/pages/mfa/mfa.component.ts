import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

import { ApiService } from '@core/services/api.service';

@Component({
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    RouterLink,
  ],
  template: `
    <h2 class="text-2xl font-medium mb-4">Autenticação em dois fatores</h2>
    @if (!enrolled()) {
      <mat-card class="p-4 max-w-lg">
        <p class="mb-3">Ative o MFA para proteger sua conta.</p>
        <button mat-raised-button color="primary" (click)="enroll()" [disabled]="loading">Gerar QR Code</button>
        @if (secret()) {
          <p class="mt-4 text-sm break-all">Secret: {{ secret() }}</p>
          <p class="text-xs text-gray-500 break-all">{{ uri() }}</p>
        }
      </mat-card>
    }
    <mat-card class="p-4 max-w-lg mt-4">
      <form [formGroup]="form" (ngSubmit)="verify()" class="grid gap-3">
        <mat-form-field appearance="outline">
          <mat-label>Código TOTP</mat-label>
          <input matInput formControlName="code" maxlength="6" />
        </mat-form-field>
        <button mat-raised-button color="accent" [disabled]="form.invalid || loading">Verificar</button>
      </form>
      @if (message()) {
        <p class="mt-2 text-green-700">{{ message() }}</p>
      }
    </mat-card>
    <a mat-button routerLink="/profile" class="mt-4 inline-block">Voltar</a>
  `,
})
export class MfaComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  enrolled = signal(false);
  secret = signal('');
  uri = signal('');
  message = signal('');
  form = this.fb.nonNullable.group({ code: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(6)]] });

  enroll(): void {
    this.loading = true;
    this.api.enrollMfa().subscribe({
      next: (data) => {
        this.secret.set(data.secret);
        this.uri.set(data.provisioning_uri);
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  verify(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.verifyMfa(this.form.controls.code.value).subscribe({
      next: () => {
        this.message.set('MFA ativado com sucesso');
        this.enrolled.set(true);
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
