import { Injectable, signal, computed } from '@angular/core';
import { AdminUser } from '../models/admin.model';

@Injectable({ providedIn: 'root' })
export class AdminAuthService {

  private readonly ACCESS_KEY  = 'admin_access_token';
  private readonly REFRESH_KEY = 'admin_refresh_token';
  private readonly USER_KEY    = 'admin_user';

  private readonly _user = signal<AdminUser | null>(this._loadUser());

  readonly user         = this._user.asReadonly();
  readonly isLogged     = computed(() => this._user() !== null);
  readonly isSuperAdmin = computed(() => this._user()?.is_super_admin ?? false);
  readonly fullName     = computed(() => {
    const u = this._user();
    return u ? `${u.user_fname} ${u.user_lname}` : '';
  });

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  saveSession(access: string, refresh: string, user: AdminUser): void {
    localStorage.setItem(this.ACCESS_KEY,  access);
    localStorage.setItem(this.REFRESH_KEY, refresh);
    localStorage.setItem(this.USER_KEY,    JSON.stringify(user));
    this._user.set(user);
  }

  updateAccessToken(access: string): void {
    localStorage.setItem(this.ACCESS_KEY, access);
  }

  clearSession(): void {
    localStorage.removeItem(this.ACCESS_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this._user.set(null);
  }

  private _loadUser(): AdminUser | null {
    try {
      const raw = localStorage.getItem(this.USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }
}
