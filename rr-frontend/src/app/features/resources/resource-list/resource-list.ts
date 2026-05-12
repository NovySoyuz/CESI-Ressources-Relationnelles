import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';
import { ResourceService } from '../services/resource.service';
import { Resource, Category, Relation, ResourceFilters } from '../../../core/models/resource.model';
import { ResourceCard } from '../../../shared/components/resource-card/resource-card';
import { FilterBar } from '../../../shared/components/filter-bar/filter-bar';

@Component({
  selector: 'app-resource-list',
  standalone: true,
  imports: [RouterLink, FormsModule, ResourceCard, FilterBar],
  templateUrl: './resource-list.html',
})
export class ResourceList implements OnInit, OnDestroy {
  private readonly service = inject(ResourceService);
  private readonly search$ = new Subject<string>();

  resources  = signal<Resource[]>([]);
  categories = signal<Category[]>([]);
  relations  = signal<Relation[]>([]);
  total      = signal(0);
  loading    = signal(false);
  error      = signal<string | null>(null);

  searchQuery      = '';
  currentFilters: ResourceFilters = {};
  ordering         = '-resource_created_at';

  ngOnInit(): void {
    this.loadResources();

    this.search$.pipe(debounceTime(300), distinctUntilChanged()).subscribe(q => {
      this.currentFilters = { ...this.currentFilters, q: q || undefined };
      this.loadResources();
    });
  }

  ngOnDestroy(): void {
    this.search$.complete();
  }

  onSearch(q: string): void {
    this.search$.next(q);
  }

  onFiltersChange(f: ResourceFilters): void {
    this.currentFilters = { ...this.currentFilters, ...f };
    this.loadResources();
  }

  onOrderingChange(event: Event): void {
    this.ordering = (event.target as HTMLSelectElement).value;
    this.loadResources();
  }

  private loadResources(): void {
    this.loading.set(true);
    this.error.set(null);
    this.service.list({ ...this.currentFilters, ordering: this.ordering }).subscribe({
      next: res => {
        this.resources.set(res.results);
        this.total.set(res.count);
        this.loading.set(false);
        this.deriveFilters(res.results);
      },
      error: () => {
        this.error.set('Erreur lors du chargement des ressources.');
        this.loading.set(false);
      },
    });
  }

  // Déduit les catégories/relations disponibles depuis les ressources chargées
  private deriveFilters(resources: Resource[]): void {
    const catMap = new Map<string, Category>();
    const relMap = new Map<string, Relation>();
    for (const r of resources) {
      for (const c of r.categories) catMap.set(c.category_id, c);
      for (const rel of r.relations) relMap.set(rel.relation_id, rel);
    }
    if (catMap.size > 0) this.categories.set(Array.from(catMap.values()));
    if (relMap.size > 0) this.relations.set(Array.from(relMap.values()));
  }
}
