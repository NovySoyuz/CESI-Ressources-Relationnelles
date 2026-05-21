import { Component, input } from '@angular/core';

@Component({
  selector: 'app-category-badge',
  standalone: true,
  template: `<p class="fr-tag fr-tag--sm">{{ label() }}</p>`,
})
export class CategoryBadge {
  readonly label = input.required<string>();
}
