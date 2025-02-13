import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {AssetViewerComponent} from '../edc-demo/components/asset-viewer/asset-viewer.component';
import {CatalogBrowserComponent} from '../edc-demo/components/catalog-browser/catalog-browser.component';
import {IntroductionComponent} from '../edc-demo/components/introduction/introduction.component';
import {
  ContractDefinitionViewerComponent
} from '../edc-demo/components/contract-definition-viewer/contract-definition-viewer.component';
import {
  TransferHistoryViewerComponent
} from '../edc-demo/components/transfer-history/transfer-history-viewer.component';
import {PolicyViewComponent} from "../edc-demo/components/policy-view/policy-view.component";
import {ContractViewerComponent} from "../edc-demo/components/contract-viewer/contract-viewer.component";
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
  {
    path: 'introduction',
    component: IntroductionComponent,
    data: {title: 'Getting Started', icon: 'info_outline'},
    canActivate: [authGuard],
  },
  {
    path: 'browse-catalog',
    component: CatalogBrowserComponent,
    data: {title: 'Catalog Browser', icon: 'sim_card'},
    canActivate: [authGuard],
  },
  {
    path: 'contracts',
    component: ContractViewerComponent,
    data: {title: 'Contracts', icon: 'attachment'},
    canActivate: [authGuard],
  },
  {
    path: 'transfer-history',
    component: TransferHistoryViewerComponent,
    data: {title: 'Transfer History', icon: 'assignment'},
    canActivate: [authGuard],
  },
  {
    path: 'contract-definitions',
    component: ContractDefinitionViewerComponent,
    data: {title: 'Contract Definitions', icon: 'rule'},
    canActivate: [authGuard],
  },
  {
    path: 'policies',
    component: PolicyViewComponent,
    data: {title: 'Policies', icon: 'policy'},
    canActivate: [authGuard],
  },
  {
    path: 'my-assets', // must not be "assets" to prevent conflict with assets directory
    component: AssetViewerComponent,
    data: {title: 'Assets', icon: 'upload'},
    canActivate: [authGuard],
  },
  {
    path: '', redirectTo: 'introduction', pathMatch: 'full',
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
