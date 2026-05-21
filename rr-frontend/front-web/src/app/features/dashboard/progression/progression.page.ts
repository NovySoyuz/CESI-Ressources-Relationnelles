import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import { InteractionService } from '../../interactions/services/interaction.service';

interface ProgressMetric {
  label: string;
  value: number;
  ratio: number;
}

@Component({
  selector: 'app-progression-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './progression.page.html',
  styleUrl: './progression.page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProgressionPageComponent {
  protected readonly isLoading = signal(true);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly summary = signal({
    likes: 0,
    favorites: 0,
    bookmarks: 0,
    exploited: 0,
    total: 0,
  });
  protected readonly metrics = computed<ProgressMetric[]>(() => {
    const summary = this.summary();
    const divisor = Math.max(summary.total, 1);

    return [
      { label: 'Likes', value: summary.likes, ratio: summary.likes / divisor },
      { label: 'Favoris', value: summary.favorites, ratio: summary.favorites / divisor },
      { label: 'Bookmarks', value: summary.bookmarks, ratio: summary.bookmarks / divisor },
      { label: 'Exploitees', value: summary.exploited, ratio: summary.exploited / divisor },
    ];
  });

  private readonly interactionService = inject(InteractionService);

  constructor() {
    this.interactionService.getSummary().subscribe({
      next: (summary) => {
        this.summary.set(summary);
        this.isLoading.set(false);
      },
      error: (error: unknown) => {
        this.errorMessage.set(getErrorMessage(error, 'Impossible de charger la progression.'));
        this.isLoading.set(false);
      },
    });
  }
}