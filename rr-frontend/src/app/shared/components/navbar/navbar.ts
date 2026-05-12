import { Component, inject, computed } from '@angular/core';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
})
export class NavbarComponent {
  readonly auth            = inject(AuthService);
  private readonly router  = inject(Router);

  readonly fullName = computed(() => {
    const u = this.auth.user();
    return u ? `${u.user_fname} ${u.user_lname}` : '';
  });

  logout(): void {
    this.auth.clearSession();
    this.router.navigate(['/resources']);
  }
}
