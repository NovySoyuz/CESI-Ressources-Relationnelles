import { Component, input, output, HostListener, ElementRef, inject } from '@angular/core';
import { Category, Relation, ResourceLabel, RESOURCE_LABEL_DISPLAY, ResourceFilters } from '../../../core/models/resource.model';

@Component({
  selector: 'app-filter-bar',
  standalone: true,
  imports: [],
  templateUrl: './filter-bar.html',
  styleUrl: './filter-bar.scss',
})
export class FilterBar {
  private readonly el = inject(ElementRef);

  readonly categories    = input<Category[]>([]);
  readonly relations     = input<Relation[]>([]);
  readonly filtersChange = output<ResourceFilters>();

  selectedCategories: string[] = [];
  selectedRelations:  string[] = [];
  selectedLabel = '';

  openPanel: 'label' | 'cat' | 'rel' | null = null;

  readonly labelOptions = Object.entries(RESOURCE_LABEL_DISPLAY) as [ResourceLabel, string][];

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.el.nativeElement.contains(event.target)) {
      this.openPanel = null;
    }
  }

  toggle(panel: 'label' | 'cat' | 'rel', event: MouseEvent): void {
    event.stopPropagation();
    this.openPanel = this.openPanel === panel ? null : panel;
  }

  selectLabel(value: string): void {
    this.selectedLabel = value;
    this.openPanel     = null;
    this.emit();
  }

  toggleCategory(id: string): void {
    this.selectedCategories = this.selectedCategories.includes(id)
      ? this.selectedCategories.filter(c => c !== id)
      : [...this.selectedCategories, id];
    this.emit();
  }

  toggleRelation(id: string): void {
    this.selectedRelations = this.selectedRelations.includes(id)
      ? this.selectedRelations.filter(r => r !== id)
      : [...this.selectedRelations, id];
    this.emit();
  }

  labelFor(value: string): string {
    return RESOURCE_LABEL_DISPLAY[value as ResourceLabel] ?? value;
  }

  reset(): void {
    this.selectedCategories = [];
    this.selectedRelations  = [];
    this.selectedLabel      = '';
    this.openPanel          = null;
    this.emit();
  }

  private emit(): void {
    this.filtersChange.emit({
      categories: this.selectedCategories.length ? this.selectedCategories : undefined,
      relations:  this.selectedRelations.length  ? this.selectedRelations  : undefined,
      label:      this.selectedLabel             || undefined,
    });
  }
}
