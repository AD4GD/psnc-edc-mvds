import {APP_INITIALIZER, NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {LayoutModule} from '@angular/cdk/layout';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatButtonModule} from '@angular/material/button';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatIconModule} from '@angular/material/icon';
import {MatListModule} from '@angular/material/list';
import {NavigationComponent} from './components/navigation/navigation.component';
import {EdcDemoModule} from '../edc-demo/edc-demo.module';
import {MAT_FORM_FIELD_DEFAULT_OPTIONS} from '@angular/material/form-field';
import {AppConfigService} from "./app-config.service";
import {MatSnackBarModule} from "@angular/material/snack-bar";
import {CONNECTOR_CATALOG_API, CONNECTOR_MANAGEMENT_API, LOCAL_STORAGE_TYPE, MINIO_STORAGE_TYPE} from "./variables";
import { EdcConnectorClient } from "@think-it-labs/edc-connector-client";
import { MatChipsModule } from '@angular/material/chips';
import { CUSTOM_PRESET, LOCATION_PRESET, PURPOSE_PRESET, TIME_INTERVAL_PRESET } from './policy-presets';
import { OBLIGATION_RULE, PERMISSION_RULE, PROHIBITION_RULE } from './policy-rule-types';
import { OAuthModule } from 'angular-oauth2-oidc';
import { MatMenuModule } from '@angular/material/menu';


@NgModule({
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    LayoutModule,
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatIconModule,
    MatListModule,
    EdcDemoModule,
    MatSnackBarModule,
    MatChipsModule,
    OAuthModule.forRoot(),
    MatMenuModule,
  ],
  declarations: [
    AppComponent,
    NavigationComponent,
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: (configService: AppConfigService) => () => configService.loadConfig(),
      deps: [AppConfigService],
      multi: true
    },
    {provide: MAT_FORM_FIELD_DEFAULT_OPTIONS, useValue: {appearance: 'outline'}},
    {
      provide: CONNECTOR_MANAGEMENT_API,
      useFactory: (s: AppConfigService) => s.getConfig()?.managementApiUrl,
      deps: [AppConfigService]
    },
    {
      provide: CONNECTOR_CATALOG_API,
      useFactory:  (s: AppConfigService) => s.getConfig()?.catalogUrl,
      deps: [AppConfigService]
    },
    {
      provide: 'HOME_CONNECTOR_STORAGE_ACCOUNT',
      useFactory: (s: AppConfigService) => s.getConfig()?.storageAccount,
      deps: [AppConfigService]
    },
    {
      provide: 'STORAGE_TYPES',
      useFactory: () => [{id: LOCAL_STORAGE_TYPE, name: "Local"}, {id: MINIO_STORAGE_TYPE, name: "Minio"}],
    },
    {
      provide: 'POLICY_PRESETS',
      useFactory: () => [TIME_INTERVAL_PRESET, LOCATION_PRESET, PURPOSE_PRESET, CUSTOM_PRESET]
    },
    {
      provide: 'POLICY_RULE_TYPES',
      useFactory: () => [PERMISSION_RULE, PROHIBITION_RULE, OBLIGATION_RULE]
    },
    {
      provide: EdcConnectorClient,
      useFactory: (s: AppConfigService) => {
        return new EdcConnectorClient.Builder()
          .managementUrl(s.getConfig()?.managementApiUrl as string)
          .federatedCatalogUrl(s.getConfig()?.catalogUrl as string)
          .build();
      },
      deps: [AppConfigService]
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
