import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {

  private readonly baseUrl = (() => {
    const platform = (globalThis as any)?.Capacitor?.getPlatform?.();
    if (platform === 'android') {
      return `http://${environment.androidApiHost}:8000`;
    }
    const loc = (globalThis as any)?.location;
    // Dev : ng serve tourne sur :4200 → l'API répond sur le port 8000 du même hôte.
    if (loc?.port === '4200') {
      return `http://${loc.hostname}:8000`;
    }
    // Prod-like : le front est servi par nginx qui proxifie /api/ vers gunicorn
    // → même origine (pas de port, pas de CORS, pas de mixed-content en HTTPS).
    return '';
  })();
  private readonly http    = inject(HttpClient);

  get<T>(path: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${path}`);
  }

  post<T>(path: string, body: unknown): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${path}`, body);
  }

  patch<T>(path: string, body: unknown): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}${path}`, body);
  }

  delete<T>(path: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${path}`);
  }
}
