import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_URL, CartResponse, OrderResponse, ProductResponse, TokenResponse, UserResponse } from '@core/models/api.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = API_URL;

  register(body: { email: string; full_name: string; password: string; phone?: string }): Observable<UserResponse> {
    return this.http.post<UserResponse>(`${this.base}/auth/register`, body);
  }

  login(body: { email: string; password: string }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.base}/auth/login`, body);
  }

  me(): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.base}/users/me`);
  }

  listProducts(): Observable<ProductResponse[]> {
    return this.http.get<ProductResponse[]>(`${this.base}/products`);
  }

  addToCart(body: { product_id: string; sku: string; quantity: number; session_id?: string }): Observable<CartResponse> {
    return this.http.post<CartResponse>(`${this.base}/orders/cart/items`, body);
  }

  getCart(cartId: string): Observable<CartResponse> {
    return this.http.get<CartResponse>(`${this.base}/orders/cart/${cartId}`);
  }

  checkout(body: unknown): Observable<OrderResponse> {
    return this.http.post<OrderResponse>(`${this.base}/orders/checkout`, body);
  }

  adminDashboard(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.base}/admin/dashboard`);
  }
}
