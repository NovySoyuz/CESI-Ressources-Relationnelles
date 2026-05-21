import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { Resource, RESOURCE_LABEL_DISPLAY } from '../../../core/models/resource.model';

@Component({
  selector: 'app-resource-card',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './resource-card.html',
})
export class ResourceCard {
  readonly resource = input.required<Resource>();
  readonly labelDisplay = RESOURCE_LABEL_DISPLAY;
}
