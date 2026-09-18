import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { forkJoin } from 'rxjs';
import { AdminRecord, UserRecord } from '../../../core/models/admin.model';
import { AdminService } from '../services/admin.service';

@Component({
  selector: 'app-admin-admins',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './admin-admins.html',
})
export class AdminAdmins implements OnInit {
  private readonly adminService = inject(AdminService);

  loading    = signal(true);
  error      = signal<string | null>(null);
  formError  = signal<string | null>(null);
  submitting = signal<string | null>(null);
  admins     = signal<AdminRecord[]>([]);
  users      = signal<UserRecord[]>([]);

  // super-admin checkbox state per user_id
  superAdminMap = signal<Record<string, boolean>>({});

  readonly nonAdminUsers = computed(() => this.users().filter(u => !u.is_admin));

  ngOnInit(): void {
    this.load();
  }

  toggleSuperAdminSelection(userId: string): void {
    this.superAdminMap.update(m => ({ ...m, [userId]: !m[userId] }));
  }

  isSuperAdminSelected(userId: string): boolean {
    return !!this.superAdminMap()[userId];
  }

  promote(user: UserRecord): void {
    if (this.submitting()) return;
    this.submitting.set(user.user_id);
    this.formError.set(null);

    this.adminService.createAdmin({
      user_id:              user.user_id,
      admin_is_super_admin: this.isSuperAdminSelected(user.user_id),
    }).subscribe({
      next: () => {
        this.submitting.set(null);
        this.reload();
      },
      error: () => {
        this.formError.set(`Impossible de promouvoir ${user.user_fname} ${user.user_lname}.`);
        this.submitting.set(null);
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
      next: () => this.reload(),
      error: () => this.error.set('Impossible de supprimer l\'administrateur.'),
    });
  }

  private load(): void {
    forkJoin({
      admins: this.adminService.listAdmins(),
      users:  this.adminService.listUsers(),
    }).subscribe({
      next: ({ admins, users }) => {
        this.admins.set(admins);
        this.users.set(users);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Impossible de charger les données.');
        this.loading.set(false);
      },
    });
  }

  private reload(): void {
    forkJoin({
      admins: this.adminService.listAdmins(),
      users:  this.adminService.listUsers(),
    }).subscribe({
      next: ({ admins, users }) => {
        this.admins.set(admins);
        this.users.set(users);
      },
    });
  }
}
