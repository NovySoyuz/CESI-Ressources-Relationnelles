import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import {
  InteractionCollection,
  InteractionSummary,
  ResourceInteractionState,
} from '../../interactions/models/interaction.models';
import { InteractionService } from '../../interactions/services/interaction.service';

interface InteractionSection {
  collection: InteractionCollection;
  label: string;
  intro: string;
  items: ResourceInteractionState[];
}

@Component({
  selector: 'app-my-interactions-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './my-interactions.page.html',
  styleUrl: './my-interactions.page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MyInteractionsPageComponent {
  protected readonly isLoading = signal(true);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly summary = signal<InteractionSummary | null>(null);
  protected readonly sections = signal<InteractionSection[]>([]);
  protected readonly totalTrackedResources = computed(() =>
    this.sections().reduce((total, section) => total + section.items.length, 0),
  );

  private readonly interactionService = inject(InteractionService);

  constructor() {
    forkJoin({
      likes: this.interactionService.listCollection('likes'),
      favoris: this.interactionService.listCollection('favoris'),
      bookmarks: this.interactionService.listCollection('bookmarks'),
      exploited: this.interactionService.listCollection('exploited'),
      summary: this.interactionService.getSummary(),
    }).subscribe({
      next: ({ likes, favoris, bookmarks, exploited, summary }) => {
        this.summary.set(summary);
        this.sections.set([
          {
            collection: 'likes',
            label: 'Likes',
            intro: 'Les ressources qui ont declenche un interet immediat.',
            items: likes,
          },
          {
            collection: 'favoris',
            label: 'Favoris',
            intro: 'Les ressources a garder dans un shortlist durable.',
            items: favoris,
          },
          {
            collection: 'bookmarks',
            label: 'Bookmarks',
            intro: 'Les contenus a reprendre plus tard, sans les perdre.',
            items: bookmarks,
          },
          {
            collection: 'exploited',
            label: 'Exploitees',
            intro: 'Les ressources deja transformees en action.',
            items: exploited,
          },
        ]);
        this.isLoading.set(false);
      },
      error: (error: unknown) => {
        this.errorMessage.set(getErrorMessage(error, 'Impossible de charger le dashboard des interactions.'));
        this.isLoading.set(false);
      },
    });
  }
}