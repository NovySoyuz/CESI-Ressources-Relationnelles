import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';
import { ResourceService } from '../services/resource.service';
import { ApiService } from '../../../core/services/api.service';
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
  private readonly api     = inject(ApiService);
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
    this.api.get<Category[]>('/api/resources/categories/').subscribe({
      next: res => this.categories.set(res),
    });
    this.api.get<Relation[]>('/api/resources/relations/').subscribe({
      next: res => this.relations.set(res),
    });

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
      },
      error: () => {
        this.error.set('Erreur lors du chargement des ressources.');
        this.loading.set(false);
      },
    });
  }
}
