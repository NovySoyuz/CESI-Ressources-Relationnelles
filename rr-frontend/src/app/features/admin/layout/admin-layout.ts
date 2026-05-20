import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AdminAuthService } from '../../../core/services/admin-auth.service';
import { AdminService } from '../services/admin.service';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './admin-layout.html',
  styleUrl: './admin-layout.scss',
})
export class AdminLayout {
  readonly adminAuth = inject(AdminAuthService);
  private readonly adminService = inject(AdminService);
  private readonly router       = inject(Router);

  logout(): void {
    this.adminService.logout().subscribe({
      complete: () => {
        this.adminAuth.clearSession();
        this.router.navigate(['/admin/login']);
      },
      error: () => {
        this.adminAuth.clearSession();
        this.router.navigate(['/admin/login']);
      },
    });
  }
}
