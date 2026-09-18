import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { switchMap } from 'rxjs';
import { Resource, RESOURCE_LABEL_DISPLAY } from '../../../core/models/resource.model';
import { ResourceService } from '../services/resource.service';
import { AuthService } from '../../../core/services/auth.service';
import { InteractionButtonsComponent } from '../../../shared/components/interaction-buttons/interaction-buttons.component';
import { CommentListComponent } from '../../comments/comment-list/comment-list.component';
import { CommentFormComponent } from '../../comments/comment-form/comment-form.component';

@Component({
  selector: 'app-resource-detail',
  standalone: true,
  imports: [RouterLink, DatePipe, InteractionButtonsComponent, CommentListComponent, CommentFormComponent],
  templateUrl: './resource-detail.html',
})
export class ResourceDetail implements OnInit {
  private readonly route   = inject(ActivatedRoute);
  private readonly router  = inject(Router);
  private readonly service = inject(ResourceService);
  readonly auth            = inject(AuthService);

  resource    = signal<Resource | null>(null);
  loading     = signal(true);
  error       = signal<string | null>(null);
  refreshKey  = signal(0);

  readonly labelDisplay = RESOURCE_LABEL_DISPLAY;

  ngOnInit(): void {
    this.route.paramMap.pipe(
      switchMap(p => this.service.get(p.get('id')!))
    ).subscribe({
      next: r  => { this.resource.set(r); this.loading.set(false); },
      error: () => { this.error.set('Ressource introuvable.'); this.loading.set(false); },
    });
  }

  isAuthor(): boolean {
    const user = this.auth.user();
    const res  = this.resource();
    return !!user && !!res && user.user_id === res.resource_author.user_id;
  }

  delete(): void {
    const res = this.resource();
    if (!res || !confirm('Supprimer cette ressource ?')) return;
    this.service.delete(res.resource_id).subscribe({
      next: () => this.router.navigate(['/resources']),
    });
  }

  publish(): void {
    const res = this.resource();
    if (!res) return;
    this.service.publish(res.resource_id).subscribe({
      next: updated => this.resource.set(updated),
    });
  }
}
