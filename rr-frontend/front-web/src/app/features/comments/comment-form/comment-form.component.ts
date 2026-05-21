import { ChangeDetectionStrategy, Component, inject, input, output, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

import { getErrorMessage } from '../../../core/utils/http-error.util';
import { ResourceComment } from '../models/comment.models';
import { CommentService } from '../services/comment.service';

@Component({
  selector: 'app-comment-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './comment-form.component.html',
  styleUrl: './comment-form.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommentFormComponent {
  readonly resourceId = input('');
  readonly submitted = output<ResourceComment>();

  protected readonly isSubmitting = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly commentControl = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.maxLength(1200)],
  });

  private readonly commentService = inject(CommentService);

  protected submit(): void {
    const resourceId = this.resourceId().trim();

    if (!resourceId) {
      this.errorMessage.set('Renseignez une ressource avant de poster.');
      return;
    }

    if (this.commentControl.invalid || this.isSubmitting()) {
      this.commentControl.markAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.commentService
      .create(resourceId, this.commentControl.getRawValue().trim())
      .pipe(finalize(() => this.isSubmitting.set(false)))
      .subscribe({
        next: (comment) => {
          this.commentControl.reset('');
          this.submitted.emit(comment);
        },
        error: (error: unknown) => {
          this.errorMessage.set(getErrorMessage(error, 'Impossible de poster le commentaire.'));
        },
      });
  }
}