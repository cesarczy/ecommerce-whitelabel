import { Routes } from '@angular/router';

export const adminRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('@admin/dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },
  {
    path: 'coupons',
    loadComponent: () => import('@admin/coupons/coupons.component').then((m) => m.CouponsComponent),
  },
  {
    path: 'store',
    loadComponent: () => import('@admin/store/store-settings.component').then((m) => m.StoreSettingsComponent),
  },
  {
    path: 'banners',
    loadComponent: () => import('@admin/banners/banners.component').then((m) => m.BannersComponent),
  },
];
