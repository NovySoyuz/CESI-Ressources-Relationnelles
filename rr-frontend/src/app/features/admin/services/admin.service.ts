import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { AdminRecord } from '../../../core/models/admin.model';
import { Resource } from '../../../core/models/resource.model';

export interface AdminCreatePayload {
  user_id:             string;
  admin_is_super_admin: boolean;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly api = inject(ApiService);

  // ── Admins ──────────────────────────────────────────────────────────────────

  listAdmins(): Observable<AdminRecord[]> {
    return this.api.get<AdminRecord[]>('/api/administration/admins/');
  }

  createAdmin(payload: AdminCreatePayload): Observable<AdminRecord> {
    return this.api.post<AdminRecord>('/api/administration/admins/', payload);
  }

  updateAdmin(id: string, is_super_admin: boolean): Observable<AdminRecord> {
    return this.api.patch<AdminRecord>(`/api/administration/admins/${id}/`, { admin_is_super_admin: is_super_admin });
  }

  deleteAdmin(id: string): Observable<void> {
    return this.api.delete<void>(`/api/administration/admins/${id}/`);
  }

  logout(): Observable<void> {
    return this.api.post<void>('/api/administration/logout/', {});
  }

  // ── Ressources ──────────────────────────────────────────────────────────────

  listResources(): Observable<Resource[]> {
    return this.api.get<Resource[]>('/api/administration/resources/');
  }

  listPendingResources(): Observable<Resource[]> {
    return this.api.get<Resource[]>('/api/administration/resources/pending/');
  }

  publishResource(id: string): Observable<Resource> {
    return this.api.patch<Resource>(`/api/administration/resources/${id}/publish/`, {});
  }

  deleteResource(id: string): Observable<void> {
    return this.api.delete<void>(`/api/administration/resources/${id}/`);
  }
}
