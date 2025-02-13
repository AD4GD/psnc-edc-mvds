import { RouterModule, Routes } from '@angular/router';
import { DataCatalogComponent } from './pages/data-catalog/data-catalog.component';
import { ParticipantsComponent } from './pages/participants/participants.component';
import { authGuard } from './core/auth/auth.guard';
import { NgModule } from '@angular/core';

export const routes: Routes = [
    {
        path: 'catalog',
        component: DataCatalogComponent,
        data: {title: 'Catalog', icon: 'dataset', category: "Home"},
        canActivate: [authGuard],
    },
    /*
    {
        path: 'dashboard',
        component: DashboardComponent,
        data: {title: 'Dashboard', icon: 'space_dashboard', category: "Home"}
    },

    {
        path: 'organization',
        component: DashboardComponent,
        data: {title: 'My Organization', icon: 'account_balance', category: "Organization"}
    },
    {
      path: 'my-offers',
      component: DataCatalogComponent,
      data: {title: 'My Data Offers', icon: 'dataset_linked', category: "Organization"}
    },
    {
        path: 'my-connectors',
        component: DashboardComponent,
        data: {title: 'My Connectors', icon: 'hexagon', category: "Organization"}
    },
    */
    {
      path: 'participants',
      component: ParticipantsComponent,
      data: {title: 'Participants', icon: 'people_outline', category: "Data Space Authority"},
      canActivate: [authGuard],
    },
    /*
    {
        path: 'connectors',
        component: DataCatalogComponent,
        data: {title: 'Connectors', icon: 'hive', category: "Data Space Authority"}
    },
    {
        path: 'profile',
        component: DataCatalogComponent,
        data: {title: 'User', icon: 'face', category: "Account"}
    },
    */
    {
        path: '', redirectTo: 'catalog', pathMatch: 'full'
    }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
