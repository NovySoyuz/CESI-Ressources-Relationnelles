import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { modoGuard } from './core/guards/modo.guard';
import { adminGuard } from './core/guards/admin.guard';
import { LayoutComponent } from './shared/components/layout/layout';

export const routes: Routes = [
  {
    path: 'admin',
    children: [
      {
        path: 'login',
        loadComponent: () =>
          import('./features/admin/auth/admin-login').then(m => m.AdminLogin),
      },
      {
        path: '',
        loadComponent: () =>
          import('./features/admin/layout/admin-layout').then(m => m.AdminLayout),
        canActivate: [adminGuard],
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/admin/dashboard/admin-dashboard').then(m => m.AdminDashboard),
          },
          {
            path: 'resources',
            loadComponent: () =>
              import('./features/admin/resources/admin-resources').then(m => m.AdminResources),
          },
          {
            path: 'admins',
            loadComponent: () =>
              import('./features/admin/admins/admin-admins').then(m => m.AdminAdmins),
          },
        ],
      },
    ],
  },
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', redirectTo: 'resources', pathMatch: 'full' },
      {
        path: 'login',
        loadComponent: () => import('./features/auth/login/login').then(m => m.Login),
      },
      {
        path: 'register',
        loadComponent: () => import('./features/auth/register/register').then(m => m.Register),
      },
      {
        path: 'resources',
        children: [
          {
            path: '',
            loadComponent: () =>
              import('./features/resources/resource-list/resource-list').then(m => m.ResourceList),
          },
          {
            path: 'new',
            loadComponent: () =>
              import('./features/resources/resource-form/resource-form').then(m => m.ResourceForm),
            canActivate: [authGuard],
          },
          {
            path: 'mine',
            loadComponent: () =>
              import('./features/resources/my-resources/my-resources').then(m => m.MyResources),
            canActivate: [authGuard],
          },
          {
            path: ':id/edit',
            loadComponent: () =>
              import('./features/resources/resource-form/resource-form').then(m => m.ResourceForm),
            canActivate: [modoGuard],
          },
          {
            path: ':id',
            loadComponent: () =>
              import('./features/resources/resource-detail/resource-detail').then(m => m.ResourceDetail),
          },
        ],
      },
      {
        path: 'dashboard',
        canActivate: [authGuard],
        children: [
          { path: '', redirectTo: 'interactions', pathMatch: 'full' },
          {
            path: 'interactions',
            loadComponent: () =>
              import('./features/dashboard/my-interactions/my-interactions.page').then(m => m.MyInteractionsPageComponent),
          },
          {
            path: 'progression',
            loadComponent: () =>
              import('./features/dashboard/progression/progression.page').then(m => m.ProgressionPageComponent),
          },
        ],
      },
      {
        path: 'moderation',
        loadComponent: () =>
          import('./features/moderation/moderation').then(m => m.Moderation),
        canActivate: [modoGuard],
      },
      { path: '**', redirectTo: 'resources' },
    ],
  },
];
