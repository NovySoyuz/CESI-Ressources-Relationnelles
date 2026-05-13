import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { modoGuard } from './core/guards/modo.guard';
import { LayoutComponent } from './shared/components/layout/layout';

export const routes: Routes = [
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
        path: 'moderation',
        loadComponent: () =>
          import('./features/moderation/moderation').then(m => m.Moderation),
        canActivate: [modoGuard],
      },
      { path: '**', redirectTo: 'resources' },
    ],
  },
];
