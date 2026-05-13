import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import { ApiService } from '../../../core/services/api.service';
import { CommentApiResponse, CommentWritePayload, ResourceComment } from '../models/comment.models';

@Injectable({ providedIn: 'root' })
export class CommentService {
  private readonly api = inject(ApiService);

  listByResource(resourceId: string): Observable<ResourceComment[]> {
    return this.api
      .get<CommentApiResponse[]>(`/interactions/comments/${resourceId}/`)
      .pipe(map((response) => response.map((comment) => this.normalizeComment(comment))));
  }

  create(resourceId: string, commentsText: string): Observable<ResourceComment> {
    return this.api
      .post<CommentApiResponse, CommentWritePayload>(`/interactions/comments/${resourceId}/`, {
        comments_text: commentsText,
      })
      .pipe(map((response) => this.normalizeComment(response)));
  }

  delete(resourceId: string, commentId: string): Observable<void> {
    return this.api.delete(`/interactions/comments/${resourceId}/${commentId}/`);
  }

  reply(commentId: string, commentsText: string): Observable<ResourceComment> {
    return this.api
      .post<CommentApiResponse, CommentWritePayload>(`/comments/${commentId}/reply/`, {
        comments_text: commentsText,
      })
      .pipe(map((response) => this.normalizeComment(response)));
  }

  private normalizeComment(response: CommentApiResponse): ResourceComment {
    return {
      id: response.comments_id,
      authorId: response.citizen_id,
      resourceId: response.resource_id,
      text: response.comments_text,
      createdAt: response.comments_created_at,
    };
  }
}