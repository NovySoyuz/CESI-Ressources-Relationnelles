import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import {
  Resource,
  PagedResponse,
  ResourceFilters,
} from '../../../core/models/resource.model';

@Injectable({ providedIn: 'root' })
export class ResourceService {
  private readonly api = inject(ApiService);

  list(filters?: ResourceFilters): Observable<PagedResponse<Resource>> {
    return this.api.get<unknown>(`/api/resources/${this._qs(filters)}`).pipe(map(this._normalize));
  }

  search(q: string, filters?: Omit<ResourceFilters, 'q'>): Observable<PagedResponse<Resource>> {
    return this.api.get<unknown>(`/api/resources/search/${this._qs({ ...filters, q })}`).pipe(map(this._normalize));
  }

  filter(filters: ResourceFilters): Observable<PagedResponse<Resource>> {
    return this.api.get<unknown>(`/api/resources/filter/${this._qs(filters)}`).pipe(map(this._normalize));
  }

  get(id: string): Observable<Resource> {
    return this.api.get<Resource>(`/api/resources/${id}/`);
  }

  create(data: Partial<Resource>): Observable<Resource> {
    return this.api.post<Resource>('/api/resources/', data);
  }

  update(id: string, data: Partial<Resource>): Observable<Resource> {
    return this.api.patch<Resource>(`/api/resources/${id}/`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/api/resources/${id}/`);
  }

  publish(id: string): Observable<Resource> {
    return this.api.patch<Resource>(`/api/resources/${id}/publish/`, {});
  }

  pending(): Observable<Resource[]> {
    return this.api.get<Resource[]>('/api/resources/pending/');
  }

  myResources(): Observable<PagedResponse<Resource>> {
    return this.api.get<unknown>('/api/resources/?author=me').pipe(map(this._normalize));
  }

  private readonly _normalize = (res: unknown): PagedResponse<Resource> => {
    if (Array.isArray(res)) return { count: res.length, results: res };
    const r = res as PagedResponse<Resource>;
    return { count: r.count ?? 0, results: r.results ?? [] };
  };

  private _qs(filters?: ResourceFilters): string {
    if (!filters) return '';
    const p = new URLSearchParams();
    filters.categories?.forEach(id => p.append('category', id));
    filters.relations?.forEach(id  => p.append('relation', id));
    if (filters.label)    p.set('label',    filters.label);
    if (filters.q)        p.set('search',   filters.q);
    if (filters.ordering) p.set('ordering', filters.ordering);
    const s = p.toString();
    return s ? `?${s}` : '';
  }
}
