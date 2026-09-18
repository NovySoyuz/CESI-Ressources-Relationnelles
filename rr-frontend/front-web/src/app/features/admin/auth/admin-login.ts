import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { AdminAuthService } from '../../../core/services/admin-auth.service';
import { AdminLoginResponse } from '../../../core/models/admin.model';

@Component({
  selector: 'app-admin-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './admin-login.html',
  styleUrl: './admin-login.scss',
})
export class AdminLogin {
  private readonly fb       = inject(FormBuilder);
  private readonly api      = inject(ApiService);
  private readonly auth     = inject(AdminAuthService);
  private readonly router   = inject(Router);

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

    this.api.post<AdminLoginResponse>('/api/administration/login/', this.form.value).subscribe({
      next: res => {
        this.auth.saveSession(res.access, res.refresh, res.user);
        this.router.navigate(['/admin']);
      },
      error: () => {
        this.error.set('Identifiants incorrects ou compte non administrateur.');
        this.loading.set(false);
      },
    });
  }
}
