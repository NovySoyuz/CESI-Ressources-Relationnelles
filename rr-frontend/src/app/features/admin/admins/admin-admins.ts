import { Component, inject, signal, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AdminRecord } from '../../../core/models/admin.model';
import { AdminService } from '../services/admin.service';

@Component({
  selector: 'app-admin-admins',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule],
  templateUrl: './admin-admins.html',
})
export class AdminAdmins implements OnInit {
  private readonly fb           = inject(FormBuilder);
  private readonly adminService = inject(AdminService);

  loading     = signal(true);
  error       = signal<string | null>(null);
  admins      = signal<AdminRecord[]>([]);
  showForm    = signal(false);
  submitting  = signal(false);
  formError   = signal<string | null>(null);

  readonly form = this.fb.group({
    user_id:             ['', [Validators.required, Validators.pattern(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    )]],
    admin_is_super_admin: [false],
  });

  ngOnInit(): void {
    this.load();
  }

  toggleForm(): void {
    this.showForm.update(v => !v);
    this.formError.set(null);
    this.form.reset({ user_id: '', admin_is_super_admin: false });
  }

  submit(): void {
    if (this.form.invalid || this.submitting()) return;
    this.submitting.set(true);
    this.formError.set(null);

    this.adminService.createAdmin({
      user_id:             this.form.value.user_id!,
      admin_is_super_admin: this.form.value.admin_is_super_admin ?? false,
    }).subscribe({
      next: created => {
        this.admins.update(list => [created, ...list]);
        this.showForm.set(false);
        this.form.reset({ user_id: '', admin_is_super_admin: false });
        this.submitting.set(false);
      },
      error: () => {
        this.formError.set('Impossible de créer l\'administrateur. Vérifiez l\'identifiant utilisateur.');
        this.submitting.set(false);
      },
    });
  }

  toggleSuperAdmin(admin: AdminRecord): void {
    this.adminService.updateAdmin(admin.admin_id, !admin.admin_is_super_admin).subscribe({
      next: updated => this.admins.update(list =>
        list.map(a => a.admin_id === admin.admin_id ? updated : a)
      ),
      error: () => this.error.set('Impossible de modifier les droits.'),
    });
  }

  delete(id: string): void {
    if (!confirm('Retirer les droits d\'administration à cet utilisateur ?')) return;
    this.adminService.deleteAdmin(id).subscribe({
      next: () => this.admins.update(list => list.filter(a => a.admin_id !== id)),
      error: () => this.error.set('Impossible de supprimer l\'administrateur.'),
    });
  }

  private load(): void {
    this.adminService.listAdmins().subscribe({
      next: list => { this.admins.set(list); this.loading.set(false); },
      error: () => { this.error.set('Impossible de charger la liste.'); this.loading.set(false); },
    });
  }
}
