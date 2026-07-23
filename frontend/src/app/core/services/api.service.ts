import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  API_URL,
  CartResponse,
  CouponResponse,
  MfaEnrollResponse,
  OrderResponse,
  PaymentResponse,
  ProductResponse,
  ReviewResponse,
  StoreSettingsResponse,
  TokenResponse,
  UserResponse,
} from '@core/models/api.models';

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

  createPayment(body: { order_id: string; method: string; provider?: string }): Observable<PaymentResponse> {
    return this.http.post<PaymentResponse>(`${this.base}/payments`, body);
  }

  listOrders(): Observable<OrderResponse[]> {
    return this.http.get<OrderResponse[]>(`${this.base}/orders`);
  }

  createCoupon(body: {
    code: string;
    discount_type: 'percent' | 'fixed';
    discount_value: number;
    min_order_amount?: string;
  }): Observable<CouponResponse> {
    return this.http.post<CouponResponse>(`${this.base}/coupons`, body);
  }

  enrollMfa(): Observable<MfaEnrollResponse> {
    return this.http.post<MfaEnrollResponse>(`${this.base}/auth/mfa/enroll`, {});
  }

  verifyMfa(code: string): Observable<{ mfa_enabled: boolean }> {
    return this.http.post<{ mfa_enabled: boolean }>(`${this.base}/auth/mfa/verify`, { code });
  }

  getStoreSettings(): Observable<StoreSettingsResponse> {
    return this.http.get<StoreSettingsResponse>(`${this.base}/store/settings`);
  }

  updateStoreSettings(body: Partial<StoreSettingsResponse>): Observable<StoreSettingsResponse> {
    return this.http.put<StoreSettingsResponse>(`${this.base}/store/settings`, body);
  }

  createReview(body: { product_id: string; rating: number; title?: string; comment: string }): Observable<ReviewResponse> {
    return this.http.post<ReviewResponse>(`${this.base}/reviews`, body);
  }

  adminDashboard(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.base}/admin/dashboard`);
  }
}
