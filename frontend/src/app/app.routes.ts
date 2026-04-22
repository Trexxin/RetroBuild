import { Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';

export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', redirectTo: 'items', pathMatch: 'full' },
      {
        path: 'items',
        loadComponent: () =>
          import('./pages/item-browser/item-browser.component').then(
            (m) => m.ItemBrowserComponent
          ),
      },
      {
        path: 'items/:id',
        loadComponent: () =>
          import('./pages/item-detail/item-detail.component').then(
            (m) => m.ItemDetailComponent
          ),
      },
      {
        path: 'plans',
        loadComponent: () =>
          import('./pages/build-plans/build-plans.component').then(
            (m) => m.BuildPlansComponent
          ),
      },
      {
        path: 'plans/new',
        loadComponent: () =>
          import('./pages/build-plan-edit/build-plan-edit.component').then(
            (m) => m.BuildPlanEditComponent
          ),
      },
      {
        path: 'plans/:id',
        loadComponent: () =>
          import('./pages/build-plan-edit/build-plan-edit.component').then(
            (m) => m.BuildPlanEditComponent
          ),
      },
      {
        path: 'analysis',
        loadComponent: () =>
          import('./pages/run-analysis/run-analysis.component').then(
            (m) => m.RunAnalysisComponent
          ),
      },
      {
        path: 'history',
        loadComponent: () =>
          import('./pages/history/history.component').then(
            (m) => m.HistoryComponent
          ),
      },
    ],
  },
];
