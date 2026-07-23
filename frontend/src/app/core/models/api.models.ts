export const API_URL = 'http://localhost:8000/api/v1';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  email_verified: boolean;
  roles: string[];
}

export interface ProductResponse {
  id: string;
  name: string;
  slug: string;
  description: string;
  sku: string;
  price: string;
  currency: string;
  status: string;
  category_id: string;
  image_url: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
}

export interface CategoryResponse {
  id: string;
  name: string;
  slug: string;
}

export interface CartResponse {
  id: string;
  items: CartItemResponse[];
  subtotal: string;
  item_count: number;
}

export interface CartItemResponse {
  id: string;
  product_id: string;
  sku: string;
  product_name: string;
  unit_price: string;
  quantity: number;
  line_total: string;
}

export interface OrderResponse {
  id: string;
  order_number: string;
  status: string;
  subtotal: string;
  discount: string;
  shipping_cost: string;
  total: string;
  items: CartItemResponse[];
}

export interface PaymentResponse {
  id: string;
  order_id: string;
  status: string;
  provider: string;
  method: string;
  amount: string;
  checkout_url: string | null;
}

export interface CouponResponse {
  id: string;
  code: string;
  discount_type: string;
  discount_value: number;
  is_active: boolean;
}

export interface ReviewResponse {
  id: string;
  product_id: string;
  rating: number;
  title: string;
  comment: string;
}

export interface StoreSettingsResponse {
  name: string;
  tagline: string;
  logo_url: string | null;
  primary_color: string;
  secondary_color: string;
}

export interface MfaEnrollResponse {
  secret: string;
  provisioning_uri: string;
}

export interface BannerResponse {
  id: string;
  title: string;
  image_url: string;
  link_url: string | null;
  sort_order: number;
}

export interface AnalyticsResponse {
  total_sales: string;
  orders_count: number;
  carts_count: number;
  customers_count: number;
  favorites_count: number;
  reviews_count: number;
  average_ticket: string;
  conversion_rate: string;
}
