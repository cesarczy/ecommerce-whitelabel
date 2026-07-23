import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';

import { ApiService } from '@core/services/api.service';
import { CategoryResponse } from '@core/models/api.models';

@Component({
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
  ],
  template: `
    <h2 class="text-xl font-medium mb-4">Cadastrar produto</h2>
    <mat-card class="p-4 max-w-2xl">
      <form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-3">
        <mat-form-field appearance="outline">
          <mat-label>Nome</mat-label>
          <input matInput formControlName="name" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Descrição</mat-label>
          <textarea matInput rows="3" formControlName="description"></textarea>
        </mat-form-field>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <mat-form-field appearance="outline">
            <mat-label>SKU</mat-label>
            <input matInput formControlName="sku" />
          </mat-form-field>
          <mat-form-field appearance="outline">
            <mat-label>Preço (R$)</mat-label>
            <input matInput type="number" step="0.01" formControlName="price" />
          </mat-form-field>
        </div>
        <mat-form-field appearance="outline">
          <mat-label>Categoria</mat-label>
          <mat-select formControlName="category_id">
            @for (category of categories(); track category.id) {
              <mat-option [value]="category.id">{{ category.name }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
        <div>
          <label class="block text-sm text-gray-600 mb-1">Imagem do produto</label>
          <input type="file" accept="image/*" (change)="onFileSelected($event)" />
        </div>
        @if (error()) {
          <p class="text-red-600 text-sm">{{ error() }}</p>
        }
        @if (message()) {
          <p class="text-green-700 text-sm">{{ message() }}</p>
        }
        <button mat-raised-button color="primary" [disabled]="form.invalid || !imageFile || loading()">
          Criar e publicar
        </button>
      </form>
    </mat-card>
    <p class="mt-4 text-sm text-gray-600">
      Produtos publicados aparecem em
      <a routerLink="/products" class="text-indigo-600">Produtos</a>.
    </p>
  `,
})
export class ProductsAdminComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);

  categories = signal<CategoryResponse[]>([]);
  loading = signal(false);
  message = signal('');
  error = signal('');
  imageFile: File | null = null;

  form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: ['', Validators.required],
    sku: ['', Validators.required],
    price: ['', [Validators.required, Validators.min(0.01)]],
    category_id: ['', Validators.required],
  });

  ngOnInit(): void {
    this.api.listCategories().subscribe({
      next: (items) => {
        this.categories.set(items);
        if (items.length > 0) {
          this.form.patchValue({ category_id: items[0].id });
        }
      },
      error: () => this.error.set('Não foi possível carregar categorias.'),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.imageFile = input.files?.[0] ?? null;
  }

  submit(): void {
    if (this.form.invalid || !this.imageFile) return;

    this.loading.set(true);
    this.error.set('');
    this.message.set('');

    const { name, description, sku, price, category_id } = this.form.getRawValue();
    this.api
      .createProduct({
        name,
        description,
        sku,
        price: String(price),
        category_id,
      })
      .subscribe({
        next: (product) => {
          this.api.uploadProductImage(product.id, this.imageFile!).subscribe({
            next: (upload) => {
              this.api.publishProduct(product.id, upload.storage_key).subscribe({
                next: (published) => {
                  this.message.set(`Produto "${published.name}" publicado com sucesso.`);
                  this.form.reset({ category_id: this.categories()[0]?.id ?? '' });
                  this.imageFile = null;
                  this.loading.set(false);
                },
                error: () => {
                  this.error.set('Produto criado, mas falhou ao publicar.');
                  this.loading.set(false);
                },
              });
            },
            error: () => {
              this.error.set('Produto criado, mas falhou ao enviar a imagem.');
              this.loading.set(false);
            },
          });
        },
        error: () => {
          this.error.set('Não foi possível criar o produto.');
          this.loading.set(false);
        },
      });
  }
}
