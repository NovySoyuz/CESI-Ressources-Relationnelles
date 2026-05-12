import { ChangeDetectionStrategy, Component, inject, input, output, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import { ResourceComment } from '../models/comment.models';
import { CommentService } from '../services/comment.service';

@Component({
  selector: 'app-comment-reply',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './comment-reply.component.html',
  styleUrl: './comment-reply.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommentReplyComponent {
  readonly commentId = input('');
  readonly replied = output<ResourceComment>();

  protected readonly isExpanded = signal(false);
  protected readonly isSubmitting = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly replyControl = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.maxLength(800)],
  });

  private readonly commentService = inject(CommentService);

  protected toggleForm(): void {
    this.errorMessage.set(null);
    this.isExpanded.update((value) => !value);
  }

  protected submit(): void {
    const commentId = this.commentId().trim();

    if (!commentId) {
      this.errorMessage.set('Le commentaire cible est manquant.');
      return;
    }

    if (this.replyControl.invalid || this.isSubmitting()) {
      this.replyControl.markAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.commentService
      .reply(commentId, this.replyControl.getRawValue().trim())
      .pipe(finalize(() => this.isSubmitting.set(false)))
      .subscribe({
        next: (comment) => {
          this.replyControl.reset('');
          this.isExpanded.set(false);
          this.replied.emit(comment);
        },
        error: (error: unknown) => {
          this.errorMessage.set(getErrorMessage(error, 'Impossible de poster la reponse.'));
        },
      });
  }
}