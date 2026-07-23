import { Routes } from '@angular/router';
import { authGuard } from '@core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('@pages/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'login',
    loadComponent: () => import('@pages/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () => import('@pages/register/register.component').then((m) => m.RegisterComponent),
  },
  {
    path: 'products',
    loadComponent: () => import('@pages/products/products.component').then((m) => m.ProductsComponent),
  },
  {
    path: 'products/:slug',
    loadComponent: () => import('@pages/product-detail/product-detail.component').then((m) => m.ProductDetailComponent),
  },
  {
    path: 'cart',
    loadComponent: () => import('@pages/cart/cart.component').then((m) => m.CartComponent),
  },
  {
    path: 'checkout',
    canActivate: [authGuard],
    loadComponent: () => import('@pages/checkout/checkout.component').then((m) => m.CheckoutComponent),
  },
  {
    path: 'profile',
    canActivate: [authGuard],
    loadComponent: () => import('@pages/profile/profile.component').then((m) => m.ProfileComponent),
  },
  {
    path: 'orders',
    canActivate: [authGuard],
    loadComponent: () => import('@pages/orders/orders.component').then((m) => m.OrdersComponent),
  },
  {
    path: 'mfa',
    canActivate: [authGuard],
    loadComponent: () => import('@pages/mfa/mfa.component').then((m) => m.MfaComponent),
  },
  {
    path: 'favorites',
    canActivate: [authGuard],
    loadComponent: () => import('@pages/favorites/favorites.component').then((m) => m.FavoritesComponent),
  },
  {
    path: 'forgot-password',
    loadComponent: () => import('@pages/forgot-password/forgot-password.component').then((m) => m.ForgotPasswordComponent),
  },
  {
    path: 'reset-password',
    loadComponent: () => import('@pages/reset-password/reset-password.component').then((m) => m.ResetPasswordComponent),
  },
  {
    path: 'verify-email',
    canActivate: [authGuard],
    loadComponent: () => import('@pages/verify-email/verify-email.component').then((m) => m.VerifyEmailComponent),
  },
  {
    path: 'admin',
    canActivate: [authGuard],
    loadChildren: () => import('@admin/admin.routes').then((m) => m.adminRoutes),
  },
  { path: '**', redirectTo: '' },
];
