import { ChangeDetectionStrategy, Component, effect, inject, input, output, signal } from '@angular/core';
import { NgClass } from '@angular/common';
import { finalize } from 'rxjs';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import {
  InteractionCountMap,
  InteractionToggleKind,
  ResourceInteractionState,
} from '../../../features/interactions/models/interaction.models';
import { InteractionService } from '../../../features/interactions/services/interaction.service';

interface InteractionAction {
  kind:      InteractionToggleKind;
  label:     string;
  iconLine:  string;
  iconFill:  string;
}

@Component({
  selector: 'app-interaction-buttons',
  standalone: true,
  imports: [NgClass],
  templateUrl: './interaction-buttons.component.html',
  styleUrl: './interaction-buttons.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InteractionButtonsComponent {
  readonly resourceId   = input('');
  readonly counts       = input<InteractionCountMap | null>(null);
  readonly initialState = input<ResourceInteractionState | null>(null);

  readonly stateChanged = output<ResourceInteractionState>();
  readonly loadFailed   = output<string>();

  protected readonly state        = signal<ResourceInteractionState | null>(null);
  protected readonly isLoading    = signal(false);
  protected readonly pendingKind  = signal<InteractionToggleKind | null>(null);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly actions: InteractionAction[] = [
    { kind: 'like',      label: 'J\'aime',          iconLine: 'fr-icon-thumb-up-line',  iconFill: 'fr-icon-thumb-up-fill'  },
    { kind: 'favorite',  label: 'Favori',            iconLine: 'fr-icon-heart-line',     iconFill: 'fr-icon-heart-fill'     },
    { kind: 'bookmark',  label: 'À lire plus tard',  iconLine: 'fr-icon-bookmark-line',  iconFill: 'fr-icon-bookmark-fill'  },
    { kind: 'exploited', label: 'Mis en pratique',   iconLine: 'fr-icon-award-line',     iconFill: 'fr-icon-award-fill'     },
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

    if (currentState === null || !resourceId || this.pendingKind() !== null) return;

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
    const s = this.state();
    if (!s) return false;
    switch (kind) {
      case 'like':      return s.liked;
      case 'favorite':  return s.favorite;
      case 'bookmark':  return s.bookmarked;
      case 'exploited': return s.exploited;
    }
  }

  protected iconClass(action: InteractionAction): string {
    return this.isActive(action.kind) ? action.iconFill : action.iconLine;
  }

  protected countFor(kind: InteractionToggleKind): number | null {
    const counts = this.counts();
    return typeof counts?.[kind] === 'number' ? counts[kind] ?? null : null;
  }
}
