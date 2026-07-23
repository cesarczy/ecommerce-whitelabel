import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  AnalyticsResponse,
  API_URL,
  BannerResponse,
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

  forgotPassword(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/auth/forgot-password`, { email });
  }

  resetPassword(body: { token: string; new_password: string }): Observable<{ password_reset: boolean }> {
    return this.http.post<{ password_reset: boolean }>(`${this.base}/auth/reset-password`, body);
  }

  verifyEmail(token: string): Observable<{ email_verified: boolean }> {
    return this.http.post<{ email_verified: boolean }>(`${this.base}/auth/verify-email`, { token });
  }

  resendVerification(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/auth/resend-verification`, {});
  }

  me(): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.base}/users/me`);
  }

  listProducts(): Observable<ProductResponse[]> {
    return this.http.get<ProductResponse[]>(`${this.base}/products`);
  }

  getProductBySlug(slug: string): Observable<ProductResponse> {
    return this.http.get<ProductResponse>(`${this.base}/products/slug/${slug}`);
  }

  getRelatedProducts(productId: string): Observable<ProductResponse[]> {
    return this.http.get<ProductResponse[]>(`${this.base}/products/${productId}/related`);
  }

  addFavorite(productId: string): Observable<{ id: string; product_id: string }> {
    return this.http.post<{ id: string; product_id: string }>(`${this.base}/favorites/${productId}`, {});
  }

  removeFavorite(productId: string): Observable<{ removed: boolean }> {
    return this.http.delete<{ removed: boolean }>(`${this.base}/favorites/${productId}`);
  }

  listFavorites(): Observable<ProductResponse[]> {
    return this.http.get<ProductResponse[]>(`${this.base}/favorites`);
  }

  listBanners(): Observable<BannerResponse[]> {
    return this.http.get<BannerResponse[]>(`${this.base}/store/banners/presigned`);
  }

  createBanner(body: { title: string; image_key: string; link_url?: string; sort_order?: number }): Observable<BannerResponse> {
    return this.http.post<BannerResponse>(`${this.base}/admin/banners`, body);
  }

  deleteBanner(bannerId: string): Observable<{ deleted: boolean }> {
    return this.http.delete<{ deleted: boolean }>(`${this.base}/admin/banners/${bannerId}`);
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

  adminAnalytics(): Observable<AnalyticsResponse> {
    return this.http.get<AnalyticsResponse>(`${this.base}/admin/analytics`);
  }
}
