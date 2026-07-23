import { Component, inject } from '@angular/core';
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
    <h2 class="text-2xl font-medium mb-4">Banners</h2>
    <mat-card class="p-4 max-w-lg">
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline"><mat-label>Título</mat-label><input matInput formControlName="title" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Image key (MinIO/R2)</mat-label><input matInput formControlName="image_key" /></mat-form-field>
        <mat-form-field appearance="outline"><mat-label>Link URL</mat-label><input matInput formControlName="link_url" /></mat-form-field>
        <button mat-raised-button color="primary" [disabled]="form.invalid || loading">Criar banner</button>
      </form>
      @if (message) { <p class="mt-3 text-green-700">{{ message }}</p> }
    </mat-card>
  `,
})
export class BannersComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  loading = false;
  message = '';
  form = this.fb.nonNullable.group({
    title: ['', Validators.required],
    image_key: ['', Validators.required],
    link_url: [''],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    const { link_url, ...rest } = this.form.getRawValue();
    this.api.createBanner({ ...rest, link_url: link_url || undefined }).subscribe({
      next: () => {
        this.message = 'Banner criado';
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
