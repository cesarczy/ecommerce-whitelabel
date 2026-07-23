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
    path: 'admin',
    canActivate: [authGuard],
    loadChildren: () => import('@admin/admin.routes').then((m) => m.adminRoutes),
  },
  { path: '**', redirectTo: '' },
];
