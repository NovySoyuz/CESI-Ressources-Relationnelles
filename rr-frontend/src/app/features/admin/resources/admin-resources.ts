import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { Resource, RESOURCE_LABEL_DISPLAY } from '../../../core/models/resource.model';
import { AdminService } from '../services/admin.service';

type StatusFilter = 'all' | 'pending' | 'published';

@Component({
  selector: 'app-admin-resources',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './admin-resources.html',
})
export class AdminResources implements OnInit {
  private readonly adminService = inject(AdminService);

  loading       = signal(true);
  error         = signal<string | null>(null);
  allResources  = signal<Resource[]>([]);
  statusFilter  = signal<StatusFilter>('all');

  readonly labelDisplay = RESOURCE_LABEL_DISPLAY as Record<string, string>;

  readonly filtered = computed(() => {
    const f = this.statusFilter();
    const all = this.allResources();
    if (f === 'pending')   return all.filter(r => !r.resource_is_visible);
    if (f === 'published') return all.filter(r =>  r.resource_is_visible);
    return all;
  });

  readonly pendingCount   = computed(() => this.allResources().filter(r => !r.resource_is_visible).length);
  readonly publishedCount = computed(() => this.allResources().filter(r =>  r.resource_is_visible).length);

  ngOnInit(): void {
    this.adminService.listResources().subscribe({
      next: resources => {
        this.allResources.set(resources);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Impossible de charger les ressources.');
        this.loading.set(false);
      },
    });
  }

  approve(id: string): void {
    this.adminService.publishResource(id).subscribe({
      next: updated => this.allResources.update(list =>
        list.map(r => r.resource_id === id ? updated : r)
      ),
      error: () => this.error.set('Impossible de valider la ressource.'),
    });
  }

  delete(id: string): void {
    if (!confirm('Supprimer définitivement cette ressource ?')) return;
    this.adminService.deleteResource(id).subscribe({
      next: () => this.allResources.update(list => list.filter(r => r.resource_id !== id)),
      error: () => this.error.set('Impossible de supprimer la ressource.'),
    });
  }

  setFilter(f: StatusFilter): void {
    this.statusFilter.set(f);
  }
}
