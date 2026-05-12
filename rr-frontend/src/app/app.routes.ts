import { Routes } from '@angular/router';
import { LayoutComponent } from './shared/components/layout/layout';

// Shell principal — toutes les pages passent par LayoutComponent
export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [],
  },
];
