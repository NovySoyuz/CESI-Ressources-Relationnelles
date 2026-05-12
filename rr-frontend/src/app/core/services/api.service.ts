import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export type ApiQueryValue = string | number | boolean | null | undefined;
export type ApiQueryParams = Record<string, ApiQueryValue>;

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  get<T>(path: string, params?: ApiQueryParams): Observable<T> {
    return this.http.get<T>(this.buildUrl(path), {
      params: this.buildParams(params),
    });
  }

  post<TResponse, TBody = unknown>(path: string, body?: TBody): Observable<TResponse> {
    return this.http.post<TResponse>(this.buildUrl(path), body);
  }

  patch<TResponse, TBody = unknown>(path: string, body?: TBody): Observable<TResponse> {
    return this.http.patch<TResponse>(this.buildUrl(path), body);
  }

  delete(path: string): Observable<void> {
    return this.http.delete<void>(this.buildUrl(path));
  }

  private buildUrl(path: string): string {
    if (path.startsWith('/')) {
      return `${this.baseUrl}${path}`;
    }

    return `${this.baseUrl}/${path}`;
  }

  private buildParams(params?: ApiQueryParams): HttpParams | undefined {
    if (!params) {
      return undefined;
    }

    let httpParams = new HttpParams();

    for (const [key, value] of Object.entries(params)) {
      if (value === null || value === undefined) {
        continue;
      }

      httpParams = httpParams.set(key, String(value));
    }

    return httpParams;
  }
}