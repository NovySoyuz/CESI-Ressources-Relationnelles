import { Component, input, output, model } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category, Relation, ResourceLabel, RESOURCE_LABEL_DISPLAY, ResourceFilters } from '../../../core/models/resource.model';

@Component({
  selector: 'app-filter-bar',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './filter-bar.html',
})
export class FilterBar {
  readonly categories = input<Category[]>([]);
  readonly relations  = input<Relation[]>([]);
  readonly filtersChange = output<ResourceFilters>();

  filters: ResourceFilters = {};

  readonly labelOptions = Object.entries(RESOURCE_LABEL_DISPLAY) as [ResourceLabel, string][];

  emit(): void {
    this.filtersChange.emit({ ...this.filters });
  }

  reset(): void {
    this.filters = {};
    this.emit();
  }
}
