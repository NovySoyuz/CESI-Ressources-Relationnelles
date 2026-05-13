import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import { ApiService } from '../../../core/services/api.service';
import {
  InteractionApiResponse,
  InteractionCollection,
  InteractionSummary,
  InteractionSummaryApiResponse,
  InteractionToggleKind,
  InteractionWritePayload,
  ResourceInteractionState,
} from '../models/interaction.models';

@Injectable({ providedIn: 'root' })
export class InteractionService {
  private readonly api = inject(ApiService);

  getResourceState(resourceId: string): Observable<ResourceInteractionState> {
    return this.api
      .get<InteractionApiResponse>(`/api/interactions/${resourceId}/`)
      .pipe(map((response) => this.normalizeState(response)));
  }

  toggle(resourceId: string, kind: InteractionToggleKind, currentState: ResourceInteractionState): Observable<ResourceInteractionState> {
    const payload: InteractionWritePayload = {
      [this.flagByKind(kind)]: !this.valueByKind(kind, currentState),
    };

    return this.updateResourceState(resourceId, payload);
  }

  updateResourceState(resourceId: string, payload: InteractionWritePayload): Observable<ResourceInteractionState> {
    return this.api
      .post<InteractionApiResponse>(`/api/interactions/${resourceId}/`, payload)
      .pipe(map((response) => this.normalizeState(response)));
  }

  listCollection(collection: InteractionCollection): Observable<ResourceInteractionState[]> {
    return this.api
      .get<InteractionApiResponse[]>(`/api/interactions/${collection}/`)
      .pipe(map((response) => response.map((item) => this.normalizeState(item))));
  }

  getSummary(): Observable<InteractionSummary> {
    return this.api
      .get<InteractionSummaryApiResponse>('/api/interactions/summary/')
      .pipe(
        map((response) => ({
          likes: response.likes,
          favorites: response.favoris,
          bookmarks: response.bookmarks,
          exploited: response.exploited,
          total: response.likes + response.favoris + response.bookmarks + response.exploited,
        })),
      );
  }

  private normalizeState(response: InteractionApiResponse): ResourceInteractionState {
    return {
      citizenId: response.citizen_id ?? null,
      resourceId: response.resource_id,
      liked: response.is_liked,
      favorite: response.is_favorise,
      bookmarked: response.is_bookmark,
      exploited: response.is_exploited,
    };
  }

  private flagByKind(kind: InteractionToggleKind): keyof InteractionWritePayload {
    switch (kind) {
      case 'like':
        return 'is_liked';
      case 'favorite':
        return 'is_favorise';
      case 'bookmark':
        return 'is_bookmark';
      case 'exploited':
        return 'is_exploited';
    }
  }

  private valueByKind(kind: InteractionToggleKind, currentState: ResourceInteractionState): boolean {
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
}