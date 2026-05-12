import { Routes } from '@angular/router';

export const routes: Routes = [
	{
		path: '',
		pathMatch: 'full',
		redirectTo: 'dashboard/progression',
	},
	{
		path: 'resource-social',
		loadComponent: () =>
			import('./features/interactions/pages/resource-engagement-page/resource-engagement.page').then(
				(module) => module.ResourceEngagementPageComponent,
			),
	},
	{
		path: 'dashboard/interactions',
		loadComponent: () =>
			import('./features/dashboard/my-interactions/my-interactions.page').then(
				(module) => module.MyInteractionsPageComponent,
			),
	},
	{
		path: 'dashboard/progression',
		loadComponent: () =>
			import('./features/dashboard/progression/progression.page').then(
				(module) => module.ProgressionPageComponent,
			),
	},
	{
		path: '**',
		redirectTo: 'dashboard/progression',
	},
];
