import { Component, inject, computed, OnInit, OnDestroy } from '@angular/core';
import { RouterLink, RouterLinkActive, Router, NavigationStart } from '@angular/router';
import { filter, Subscription } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
  styleUrl: './navbar.scss',
})
export class NavbarComponent implements OnInit, OnDestroy {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private routerSub?: Subscription;

  readonly fullName = computed(() => {
    const u = this.auth.user();
    return u ? `${u.user_fname} ${u.user_lname}` : '';
  });

  ngOnInit(): void {
    this.routerSub = this.router.events.pipe(
      filter(e => e instanceof NavigationStart)
    ).subscribe(() => this.closeDsfrMenu());
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
  }

  logout(): void {
    this.auth.clearSession();
    this.router.navigate(['/resources']);
  }

  private closeDsfrMenu(): void {
    const modal = document.getElementById('header-nav-modal');
    if (modal?.dataset['frOpened'] !== 'true') return;

    const closeBtn = modal.querySelector<HTMLElement>('.fr-link--close');
    if (closeBtn) {
      closeBtn.click();
    } else {
      modal.dataset['frOpened'] = 'false';
      document.documentElement.classList.remove('fr-overflow');
    }
  }
}
