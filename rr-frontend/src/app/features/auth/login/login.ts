import { Component, inject, signal } from '@angular/core';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { AuthService, AuthUser } from '../../../core/services/auth.service';

interface LoginResponse {
  access:  string;
  refresh: string;
  user:    AuthUser;
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
})
export class Login {
  private readonly fb     = inject(FormBuilder);
  private readonly api    = inject(ApiService);
  private readonly auth   = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route  = inject(ActivatedRoute);

  loading = signal(false);
  error   = signal<string | null>(null);

  readonly form = this.fb.group({
    user_mail: ['', [Validators.required, Validators.email]],
    password:  ['', Validators.required],
  });

  submit(): void {
    if (this.form.invalid) return;
    this.loading.set(true);
    this.error.set(null);

    this.api.post<LoginResponse>('/api/auth/login/', this.form.value).subscribe({
      next: res => {
        this.auth.saveSession(res.access, res.refresh, res.user);
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') ?? '/resources';
        this.router.navigateByUrl(returnUrl);
      },
      error: () => {
        this.error.set('Identifiants incorrects.');
        this.loading.set(false);
      },
    });
  }
}
