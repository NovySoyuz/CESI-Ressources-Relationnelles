import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';

export const refreshInterceptor: HttpInterceptorFn = (req, next) => {
  const auth   = inject(AuthService);
  const api    = inject(ApiService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {

      // On ne tente le refresh que sur un 401
      // et jamais sur la route refresh elle-même (évite la boucle infinie)
      if (error.status !== 401 || req.url.includes('/api/auth/refresh/')) {
        return throwError(() => error);
      }

      const refreshToken = auth.getRefreshToken();
      if (!refreshToken) {
        auth.clearSession();
        router.navigate(['/login']);
        return throwError(() => error);
      }

      // Appel refresh → nouveau access token → rejoue la requête originale
      return api.post<{ access: string }>('/api/auth/refresh/', { refresh: refreshToken }).pipe(
        switchMap(({ access }) => {
          auth.updateAccessToken(access);
          return next(req.clone({
            setHeaders: { Authorization: `Bearer ${access}` }
          }));
        }),
        catchError((refreshError) => {
          // Refresh expiré ou révoqué → déconnexion forcée
          auth.clearSession();
          router.navigate(['/login']);
          return throwError(() => refreshError);
        })
      );
    })
  );
};
