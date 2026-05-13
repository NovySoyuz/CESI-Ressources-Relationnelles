import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { Resource, RESOURCE_LABEL_DISPLAY, ResourceLabel } from '../../core/models/resource.model';
import { ResourceService } from '../resources/services/resource.service';

@Component({
  selector: 'app-moderation',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './moderation.html',
})
export class Moderation implements OnInit {
  private readonly service = inject(ResourceService);

  resources = signal<Resource[]>([]);
  loading   = signal(true);
  error     = signal<string | null>(null);

  readonly labelDisplay = RESOURCE_LABEL_DISPLAY as Record<string, string>;

  ngOnInit(): void {
    this.load();
  }

  approve(id: string): void {
    this.service.publish(id).subscribe({
      next: () => this.resources.update(list => list.filter(r => r.resource_id !== id)),
      error: () => this.error.set('Impossible d\'approuver la ressource.'),
    });
  }

  reject(id: string): void {
    this.service.delete(id).subscribe({
      next: () => this.resources.update(list => list.filter(r => r.resource_id !== id)),
      error: () => this.error.set('Impossible de supprimer la ressource.'),
    });
  }

  private load(): void {
    this.loading.set(true);
    this.service.pending().subscribe({
      next:  res => { this.resources.set(res); this.loading.set(false); },
      error: ()  => { this.error.set('Impossible de charger les ressources en attente.'); this.loading.set(false); },
    });
  }
}
