import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { AdminAuthService } from '../services/admin-auth.service';
import { ApiService } from '../services/api.service';

export const refreshInterceptor: HttpInterceptorFn = (req, next) => {
  const auth      = inject(AuthService);
  const adminAuth = inject(AdminAuthService);
  const api       = inject(ApiService);
  const router    = inject(Router);

  const isAdminUrl = req.url.includes('/api/administration/');

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {

      if (
        error.status !== 401 ||
        req.url.includes('/api/auth/refresh/') ||
        req.url.includes('/api/administration/refresh/')
      ) {
        return throwError(() => error);
      }

      if (isAdminUrl) {
        const refreshToken = adminAuth.getRefreshToken();
        if (!refreshToken) {
          adminAuth.clearSession();
          router.navigate(['/admin/login']);
          return throwError(() => error);
        }

        return api.post<{ access: string }>('/api/administration/refresh/', { refresh: refreshToken }).pipe(
          switchMap(({ access }) => {
            adminAuth.updateAccessToken(access);
            return next(req.clone({
              setHeaders: { Authorization: `Bearer ${access}` }
            }));
          }),
          catchError((refreshError) => {
            adminAuth.clearSession();
            router.navigate(['/admin/login']);
            return throwError(() => refreshError);
          })
        );
      }

      const refreshToken = auth.getRefreshToken();
      if (!refreshToken) {
        auth.clearSession();
        router.navigate(['/login']);
        return throwError(() => error);
      }

      return api.post<{ access: string }>('/api/auth/refresh/', { refresh: refreshToken }).pipe(
        switchMap(({ access }) => {
          auth.updateAccessToken(access);
          return next(req.clone({
            setHeaders: { Authorization: `Bearer ${access}` }
          }));
        }),
        catchError((refreshError) => {
          auth.clearSession();
          router.navigate(['/login']);
          return throwError(() => refreshError);
        })
      );
    })
  );
};
