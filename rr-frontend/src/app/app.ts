import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  protected readonly title = 'Marianne';
  protected readonly serviceTagline = 'Ressources documentaires et interactions citoyennes';

  protected readonly navigation = [
    {
      label: 'Progression',
      link: '/dashboard/progression',
    },
    {
      label: 'Mes interactions',
      link: '/dashboard/interactions',
    },
    {
      label: 'Ressource sociale',
      link: '/resource-social',
    },
  ];
}
