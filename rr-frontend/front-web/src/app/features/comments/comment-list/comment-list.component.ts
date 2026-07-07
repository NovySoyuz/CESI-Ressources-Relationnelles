import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, effect, inject, input, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import { AuthService } from '../../../core/services/auth.service';
import { CommentReplyComponent } from '../comment-reply/comment-reply.component';
import { ResourceComment } from '../models/comment.models';
import { CommentService } from '../services/comment.service';

@Component({
  selector: 'app-comment-list',
  standalone: true,
  imports: [CommentReplyComponent, DatePipe],
  templateUrl: './comment-list.component.html',
  styleUrl: './comment-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommentListComponent {
  readonly resourceId = input('');
  readonly refreshKey = input(0);

  protected readonly comments = signal<ResourceComment[]>([]);
  protected readonly isLoading = signal(false);
  protected readonly deletingCommentId = signal<string | null>(null);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly rootComments = computed(() =>
    this.comments().filter((c) => c.parentId === null)
  );

  private readonly commentService = inject(CommentService);
  private readonly auth = inject(AuthService);

  protected readonly currentUserId = computed(() => this.auth.user()?.user_id ?? null);

  constructor() {
    effect((onCleanup) => {
      const resourceId = this.resourceId().trim();
      this.refreshKey();

      this.errorMessage.set(null);

      if (!resourceId) {
        this.comments.set([]);
        return;
      }

      this.isLoading.set(true);
      const subscription = this.commentService
        .listByResource(resourceId)
        .pipe(finalize(() => this.isLoading.set(false)))
        .subscribe({
          next: (comments) => this.comments.set(comments),
          error: (error: unknown) => {
            this.errorMessage.set(getErrorMessage(error, 'Impossible de charger les commentaires.'));
          },
        });

      onCleanup(() => subscription.unsubscribe());
    });
  }

  protected repliesFor(parentId: string): ResourceComment[] {
    return this.comments().filter((c) => c.parentId === parentId);
  }

  protected deleteComment(comment: ResourceComment): void {
    const resourceId = this.resourceId().trim();
    if (!resourceId || this.deletingCommentId() !== null) return;

    this.errorMessage.set(null);
    this.deletingCommentId.set(comment.id);

    this.commentService
      .delete(resourceId, comment.id)
      .pipe(finalize(() => this.deletingCommentId.set(null)))
      .subscribe({
        next: () => {
          this.comments.update((items) =>
            items.filter((item) => item.id !== comment.id && item.parentId !== comment.id)
          );
        },
        error: (error: unknown) => {
          this.errorMessage.set(getErrorMessage(error, 'Impossible de supprimer ce commentaire.'));
        },
      });
  }

  protected handleReply(comment: ResourceComment): void {
    this.comments.update((items) => [...items, comment]);
  }

  protected shortAuthor(authorId: string): string {
    return `${authorId.slice(0, 8)}…`;
  }
}