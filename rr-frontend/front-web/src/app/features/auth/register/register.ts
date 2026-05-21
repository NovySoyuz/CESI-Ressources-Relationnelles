import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.html',
})
export class Register {
  private readonly fb     = inject(FormBuilder);
  private readonly api    = inject(ApiService);
  private readonly router = inject(Router);

  loading = signal(false);
  error   = signal<string | null>(null);

  readonly form = this.fb.group({
    user_fname: ['', Validators.required],
    user_lname: ['', Validators.required],
    user_mail:  ['', [Validators.required, Validators.email]],
    password:   ['', [Validators.required, Validators.minLength(8)]],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading.set(true);
    this.error.set(null);

    this.api.post('/api/auth/register/', this.form.value).subscribe({
      next: () => this.router.navigate(['/login']),
      error: (err) => {
        const msg = err?.error?.user_mail?.[0] ?? err?.error?.password?.[0] ?? 'Une erreur est survenue.';
        this.error.set(msg);
        this.loading.set(false);
      },
    });
  }
}
