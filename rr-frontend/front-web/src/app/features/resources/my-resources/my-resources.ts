import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { Resource, RESOURCE_LABEL_DISPLAY } from '../../../core/models/resource.model';
import { ResourceService } from '../services/resource.service';

@Component({
  selector: 'app-my-resources',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './my-resources.html',
})
export class MyResources implements OnInit {
  private readonly service = inject(ResourceService);

  resources = signal<Resource[]>([]);
  loading   = signal(true);
  error     = signal<string | null>(null);

  readonly labelDisplay = RESOURCE_LABEL_DISPLAY;

  ngOnInit(): void {
    this.service.myResources().subscribe({
      next:  res => { this.resources.set(res.results); this.loading.set(false); },
      error: ()  => { this.error.set('Erreur lors du chargement.'); this.loading.set(false); },
    });
  }

  publish(id: string): void {
    this.service.publish(id).subscribe({
      next: updated => this.resources.update(list => list.map(r => r.resource_id === id ? updated : r)),
    });
  }

  delete(id: string): void {
    if (!confirm('Supprimer cette ressource définitivement ?')) return;
    this.service.delete(id).subscribe({
      next: () => this.resources.update(list => list.filter(r => r.resource_id !== id)),
    });
  }
}
