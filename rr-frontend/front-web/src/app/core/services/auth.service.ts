import { Injectable, signal, computed } from '@angular/core';

export interface AuthUser {
  user_id:     string;
  user_fname:  string;
  user_lname:  string;
  user_mail:   string;
  user_is_modo: boolean;
}

@Injectable({ providedIn: 'root' })
export class AuthService {

  private readonly ACCESS_KEY  = 'access_token';
  private readonly REFRESH_KEY = 'refresh_token';
  private readonly USER_KEY    = 'auth_user';

  // Signal réactif — composants peuvent s'y abonner
  private readonly _user = signal<AuthUser | null>(this._loadUser());

  readonly user     = this._user.asReadonly();
  readonly isLogged = computed(() => this._user() !== null);
  readonly isModo   = computed(() => this._user()?.user_is_modo ?? false);

  // ── Tokens ────────────────────────────────────────────────────────────

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  // ── Session ───────────────────────────────────────────────────────────

  saveSession(access: string, refresh: string, user: AuthUser): void {
    localStorage.setItem(this.ACCESS_KEY,  access);
    localStorage.setItem(this.REFRESH_KEY, refresh);
    localStorage.setItem(this.USER_KEY,    JSON.stringify(user));
    this._user.set(user);
  }

  updateAccessToken(access: string): void {
    localStorage.setItem(this.ACCESS_KEY, access);
  }

  updateUser(partial: Partial<AuthUser>): void {
    const current = this._user();
    if (!current) return;
    const updated = { ...current, ...partial };
    localStorage.setItem(this.USER_KEY, JSON.stringify(updated));
    this._user.set(updated);
  }

  clearSession(): void {
    localStorage.removeItem(this.ACCESS_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this._user.set(null);
  }

  // ── Helpers privés ────────────────────────────────────────────────────

  private _loadUser(): AuthUser | null {
    try {
      const raw = localStorage.getItem(this.USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }
}
