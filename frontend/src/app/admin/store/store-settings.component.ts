import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

import { ApiService } from '@core/services/api.service';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <h2 class="text-2xl font-medium mb-4">Configurações da loja</h2>
    <mat-card class="p-4 max-w-lg">
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>Nome</mat-label><input matInput formControlName="name" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Tagline</mat-label><input matInput formControlName="tagline" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Cor primária</mat-label><input matInput formControlName="primary_color" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Cor secundária</mat-label><input matInput formControlName="secondary_color" /></mat-form-field>
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Salvar</button>
      </form>
      @if (message) {
        <p class="mt-3 text-green-700">{{ message }}</p>
      }
    </mat-card>
  `,
})
export class StoreSettingsComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    tagline: [''],
    primary_color: ['#4F46E5', Validators.required],
    secondary_color: ['#6366F1', Validators.required],
  });

  ngOnInit(): void {
    this.api.getStoreSettings().subscribe({
      next: (settings) => this.form.patchValue(settings),
    });
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.api.updateStoreSettings(this.form.getRawValue()).subscribe({
      next: () => {
        this.message = 'Configurações salvas';
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
