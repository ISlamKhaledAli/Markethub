import { Routes } from '@angular/router';
import { MainLayoutComponent } from './core/layouts/main-layout/main-layout';
import { roleGuard } from './core/guards/role-guard';

export const routes: Routes = [
  {
    path: 'auth',
    children: [
      {
        path: 'login',
        loadComponent: () => import('./features/auth/login/login').then((m) => m.LoginComponent),
      },
      {
        path: 'register',
        loadComponent: () =>
          import('./features/auth/register/register').then((m) => m.RegisterComponent),
      },
      { path: '', redirectTo: 'login', pathMatch: 'full' },
    ],
  },
  {
    path: 'verify-email/:token',
    loadComponent: () =>
      import('./features/auth/verify-email/verify-email').then((m) => m.VerifyEmailComponent),
  },
  {
    path: 'verify_email/:token',
    loadComponent: () =>
      import('./features/auth/verify-email/verify-email').then((m) => m.VerifyEmailComponent),
  },
  {
    path: '',
    component: MainLayoutComponent,
    children: [],
  },
  {
    path: 'seller',
    canActivate: [roleGuard(['seller', 'admin'])],
    loadComponent: () => import('./features/auth/login/login').then((m) => m.LoginComponent), // مؤقتاً حتى نبنيها
  },
  {
    path: 'admin',
    canActivate: [roleGuard(['admin'])],
    loadComponent: () => import('./features/auth/login/login').then((m) => m.LoginComponent), // مؤقتاً حتى نبنيها
  },

  // Fallback Route
  { path: '**', redirectTo: '' },
];
