import { ChangeDetectionStrategy, Component, effect, inject, input, output, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import {
  InteractionCountMap,
  InteractionToggleKind,
  ResourceInteractionState,
} from '../../../features/interactions/models/interaction.models';
import { InteractionService } from '../../../features/interactions/services/interaction.service';

interface InteractionAction {
  kind: InteractionToggleKind;
  label: string;
  caption: string;
}

@Component({
  selector: 'app-interaction-buttons',
  standalone: true,
  templateUrl: './interaction-buttons.component.html',
  styleUrl: './interaction-buttons.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InteractionButtonsComponent {
  readonly resourceId = input('');
  readonly counts = input<InteractionCountMap | null>(null);
  readonly initialState = input<ResourceInteractionState | null>(null);

  readonly stateChanged = output<ResourceInteractionState>();
  readonly loadFailed = output<string>();

  protected readonly state = signal<ResourceInteractionState | null>(null);
  protected readonly isLoading = signal(false);
  protected readonly pendingKind = signal<InteractionToggleKind | null>(null);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly actions: InteractionAction[] = [
    {
      kind: 'like',
      label: 'Like',
      caption: 'Interet rapide',
    },
    {
      kind: 'favorite',
      label: 'Favori',
      caption: 'A garder proche',
    },
    {
      kind: 'bookmark',
      label: 'Bookmark',
      caption: 'A revoir plus tard',
    },
    {
      kind: 'exploited',
      label: 'Exploitee',
      caption: 'Deja mise en pratique',
    },
  ];

  private readonly interactionService = inject(InteractionService);

  constructor() {
    effect((onCleanup) => {
      const resourceId = this.resourceId().trim();
      const seed = this.initialState();

      this.errorMessage.set(null);

      if (!resourceId) {
        this.state.set(null);
        return;
      }

      if (seed !== null && seed.resourceId === resourceId) {
        this.state.set(seed);
      }

      this.isLoading.set(true);
      const subscription = this.interactionService
        .getResourceState(resourceId)
        .pipe(finalize(() => this.isLoading.set(false)))
        .subscribe({
          next: (state) => {
            this.state.set(state);
            this.stateChanged.emit(state);
          },
          error: (error: unknown) => {
            const message = getErrorMessage(error, 'Impossible de charger les interactions.');
            this.errorMessage.set(message);
            this.loadFailed.emit(message);
          },
        });

      onCleanup(() => subscription.unsubscribe());
    });
  }

  protected toggle(kind: InteractionToggleKind): void {
    const currentState = this.state();
    const resourceId = this.resourceId().trim();

    if (currentState === null || !resourceId || this.pendingKind() !== null) {
      return;
    }

    this.errorMessage.set(null);
    this.pendingKind.set(kind);

    this.interactionService
      .toggle(resourceId, kind, currentState)
      .pipe(finalize(() => this.pendingKind.set(null)))
      .subscribe({
        next: (state) => {
          this.state.set(state);
          this.stateChanged.emit(state);
        },
        error: (error: unknown) => {
          this.errorMessage.set(getErrorMessage(error, 'Impossible de modifier cette interaction.'));
        },
      });
  }

  protected isActive(kind: InteractionToggleKind): boolean {
    const currentState = this.state();

    if (currentState === null) {
      return false;
    }

    switch (kind) {
      case 'like':
        return currentState.liked;
      case 'favorite':
        return currentState.favorite;
      case 'bookmark':
        return currentState.bookmarked;
      case 'exploited':
        return currentState.exploited;
    }
  }

  protected countFor(kind: InteractionToggleKind): number | null {
    const counts = this.counts();
    return typeof counts?.[kind] === 'number' ? counts[kind] ?? null : null;
  }
}