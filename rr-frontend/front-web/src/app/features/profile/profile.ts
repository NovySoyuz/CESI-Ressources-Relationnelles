import { Component, inject, signal, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

interface ProfileData {
  user_id:         string;
  user_fname:      string;
  user_lname:      string;
  user_mail:       string;
  user_is_modo:    boolean;
  user_is_actived: boolean;
  user_created_at: string;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile implements OnInit {
  private readonly api    = inject(ApiService);
  private readonly auth   = inject(AuthService);
  private readonly router = inject(Router);
  private readonly fb     = inject(FormBuilder);

  profile      = signal<ProfileData | null>(null);
  loadError    = signal<string | null>(null);
  showEditForm = signal(false);
  showPwdForm  = signal(false);
  editSuccess  = signal(false);
  pwdSuccess   = signal(false);
  editError    = signal<string | null>(null);
  pwdError     = signal<string | null>(null);
  editSaving   = signal(false);
  pwdSaving    = signal(false);
  deleteConfirm = signal(false);

  readonly editForm = this.fb.group({
    user_fname: ['', [Validators.required, Validators.minLength(1)]],
    user_lname: ['', [Validators.required, Validators.minLength(1)]],
  });

  readonly pwdForm = this.fb.group({
    current_password: ['', Validators.required],
    new_password:     ['', [Validators.required, Validators.minLength(8)]],
  });

  ngOnInit(): void {
    this.api.get<ProfileData>('/api/auth/me/').subscribe({
      next: data => {
        this.profile.set(data);
        this.editForm.patchValue({ user_fname: data.user_fname, user_lname: data.user_lname });
      },
      error: () => this.loadError.set('Impossible de charger le profil.'),
    });
  }

  toggleEdit(): void {
    this.showEditForm.update(v => !v);
    this.editSuccess.set(false);
    this.editError.set(null);
    const p = this.profile();
    if (p) this.editForm.patchValue({ user_fname: p.user_fname, user_lname: p.user_lname });
  }

  saveProfile(): void {
    if (this.editForm.invalid || this.editSaving()) return;
    this.editSaving.set(true);
    this.editError.set(null);

    this.api.patch<ProfileData>('/api/auth/me/', this.editForm.value).subscribe({
      next: updated => {
        this.profile.set(updated);
        this.auth.updateUser({ user_fname: updated.user_fname, user_lname: updated.user_lname });
        this.editSaving.set(false);
        this.editSuccess.set(true);
        this.showEditForm.set(false);
      },
      error: (err) => {
        this.editError.set(err?.error?.error ?? 'Impossible de mettre à jour le profil.');
        this.editSaving.set(false);
      },
    });
  }

  togglePwd(): void {
    this.showPwdForm.update(v => !v);
    this.pwdSuccess.set(false);
    this.pwdError.set(null);
    this.pwdForm.reset();
  }

  savePassword(): void {
    if (this.pwdForm.invalid || this.pwdSaving()) return;
    this.pwdSaving.set(true);
    this.pwdError.set(null);

    this.api.patch<ProfileData>('/api/auth/me/', this.pwdForm.value).subscribe({
      next: () => {
        this.pwdSaving.set(false);
        this.pwdSuccess.set(true);
        this.showPwdForm.set(false);
        this.pwdForm.reset();
      },
      error: (err) => {
        this.pwdError.set(err?.error?.error ?? 'Impossible de modifier le mot de passe.');
        this.pwdSaving.set(false);
      },
    });
  }

  deleteAccount(): void {
    this.api.delete<void>('/api/auth/me/').subscribe({
      next: () => {
        this.auth.clearSession();
        this.router.navigate(['/']);
      },
      error: () => alert('Impossible de supprimer le compte. Réessayez.'),
    });
  }
}
