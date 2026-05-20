import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AdminService } from '../services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './admin-dashboard.html',
})
export class AdminDashboard implements OnInit {
  private readonly adminService = inject(AdminService);

  loading         = signal(true);
  error           = signal<string | null>(null);
  totalResources  = signal(0);
  pendingCount    = signal(0);
  publishedCount  = signal(0);
  adminsCount     = signal(0);

  ngOnInit(): void {
    forkJoin({
      all:     this.adminService.listResources(),
      pending: this.adminService.listPendingResources(),
      admins:  this.adminService.listAdmins(),
    }).subscribe({
      next: ({ all, pending, admins }) => {
        this.totalResources.set(all.length);
        this.pendingCount.set(pending.length);
        this.publishedCount.set(all.length - pending.length);
        this.adminsCount.set(admins.length);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Impossible de charger les statistiques.');
        this.loading.set(false);
      },
    });
  }
}
