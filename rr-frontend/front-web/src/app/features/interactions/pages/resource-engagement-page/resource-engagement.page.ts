import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { CommentFormComponent } from '../../../comments/comment-form/comment-form.component';
import { CommentListComponent } from '../../../comments/comment-list/comment-list.component';
import { ResourceComment } from '../../../comments/models/comment.models';
import { InteractionButtonsComponent } from '../../../../shared/components/interaction-buttons/interaction-buttons.component';
import { ResourceInteractionState } from '../../models/interaction.models';

interface DocumentaryResourceCard {
  title: string;
  description: string;
  theme: string;
  audience: string;
  format: string;
}

@Component({
  selector: 'app-resource-engagement-page',
  standalone: true,
  imports: [ReactiveFormsModule, CommentFormComponent, CommentListComponent, InteractionButtonsComponent],
  templateUrl: './resource-engagement.page.html',
  styleUrl: './resource-engagement.page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourceEngagementPageComponent {
  protected readonly documentaryResources: DocumentaryResourceCard[] = [
    {
      title: 'Guide de mediation documentaire',
      description: 'Un parcours de lecture pour orienter un public vers des ressources fiables, accessibles et reutilisables.',
      theme: 'Guide',
      audience: 'Professionnels',
      format: 'PDF · 24 pages',
    },
    {
      title: 'Fiche pratique accessibilite et RGAA',
      description: 'Les verifications de contraste, de structure et de lisibilite a appliquer avant toute mise en ligne.',
      theme: 'Accessibilite',
      audience: 'Equipes produit',
      format: 'Checklist · 8 points',
    },
    {
      title: 'Bibliographie commentee de l accompagnement',
      description: 'Une selection de ressources de reference pour structurer un accompagnement relationnel continu.',
      theme: 'Bibliographie',
      audience: 'Citoyens',
      format: 'Dossier · 12 references',
    },
    {
      title: 'Kit d animation pour atelier documentaire',
      description: 'Des supports concrets pour animer un atelier collectif autour du tri, du partage et de la mise en pratique.',
      theme: 'Atelier',
      audience: 'Associations',
      format: 'Kit · Slides + fiche',
    },
    {
      title: 'Note de cadrage partenariale',
      description: 'Un format court pour aligner les acteurs sur les objectifs, les roles et les indicateurs de suivi.',
      theme: 'Pilotage',
      audience: 'Collectivites',
      format: 'Note · 2 pages',
    },
    {
      title: 'Parcours d entree en relation',
      description: 'Une trame documentaire simple pour guider la premiere prise de contact et capitaliser les besoins exprimes.',
      theme: 'Parcours',
      audience: 'Services publics',
      format: 'Mode operatoire',
    },
  ];

  protected readonly resourceIdControl = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required],
  });
  protected readonly activeResourceId = signal('');
  protected readonly refreshKey = signal(0);
  protected readonly lastInteraction = signal<ResourceInteractionState | null>(null);
  protected readonly lastComment = signal<ResourceComment | null>(null);

  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  constructor() {
    this.route.queryParamMap.subscribe((params) => {
      const resourceId = params.get('resourceId')?.trim() ?? '';
      this.resourceIdControl.setValue(resourceId, { emitEvent: false });
      this.activeResourceId.set(resourceId);
      this.refreshKey.update((value) => value + 1);
    });
  }

  protected applyResource(): void {
    if (this.resourceIdControl.invalid) {
      this.resourceIdControl.markAsTouched();
      return;
    }

    const resourceId = this.resourceIdControl.getRawValue().trim();
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { resourceId },
      queryParamsHandling: 'merge',
    });
  }

  protected handleInteractionChange(state: ResourceInteractionState): void {
    this.lastInteraction.set(state);
  }

  protected handleCommentCreated(comment: ResourceComment): void {
    this.lastComment.set(comment);
    this.refreshKey.update((value) => value + 1);
  }
}