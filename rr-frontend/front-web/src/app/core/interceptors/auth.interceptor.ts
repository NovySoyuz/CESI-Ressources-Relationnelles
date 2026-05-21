import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { AdminAuthService } from '../services/admin-auth.service';

const AUTH_ENDPOINTS = ['/login/', '/refresh/', '/logout/'];

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth      = inject(AuthService);
  const adminAuth = inject(AdminAuthService);

  if (AUTH_ENDPOINTS.some(e => req.url.endsWith(e))) {
    return next(req);
  }

  const token = req.url.includes('/api/administration/')
    ? adminAuth.getAccessToken()
    : auth.getAccessToken();

  if (!token) return next(req);

  return next(req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  }));
};
