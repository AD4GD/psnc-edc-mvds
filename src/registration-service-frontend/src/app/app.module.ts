import { APP_INITIALIZER, NgModule, provideZoneChangeDetection } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatOptionModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { OAuthModule, OAuthService } from 'angular-oauth2-oidc';
import { AppComponent } from './app.component';
import { MvdSidebarComponent } from './common/mvd-sidebar/mvd-sidebar.component';
import { ConfirmationDialogComponent } from './common/confirmation-dialog/confirmation-dialog.component';
import { AppConfigService } from './app.config.service';
import { provideRouter, RouterModule } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClient, provideHttpClient } from '@angular/common/http';
import { routes } from './app-routes.module';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { RegistrationServiceClient } from './core/api/services/impl/registration-service-client';
import { getClient } from './core/api/services/factories/api-factories';
import { EdcConnectorClient } from '@think-it-labs/edc-connector-client';
import { BACKEND_API_TOKEN, CATALOG_API_TOKEN } from './injection-tokens';
import { MatMenuModule } from '@angular/material/menu';
import { AddParticipantDialogComponent } from './pages/participants/components/add-participant-dialog/add-participant-dialog.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  imports: [
    BrowserModule,
    MatMenuModule,
    MatListModule,
    MatSidenavModule,
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatOptionModule,
    MatChipsModule,
    MatSnackBarModule,
    OAuthModule.forRoot(),
    RouterModule,
    BrowserAnimationsModule
  ],
  declarations: [
    // common
    AppComponent,
    MvdSidebarComponent,
    ConfirmationDialogComponent,
    // specific
    AddParticipantDialogComponent,

  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: (configService: AppConfigService) => () => configService.loadConfig(),
      deps: [AppConfigService],
      multi: true
    },
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimationsAsync(),
    provideHttpClient(),
    {
      provide: APP_INITIALIZER,
      useFactory: (configService: AppConfigService) => () => configService.loadConfig(),
      deps: [AppConfigService],
      multi: true
    },
    {
      provide: RegistrationServiceClient,
      useFactory: getClient,
      deps: [AppConfigService, EdcConnectorClient, OAuthService, HttpClient]
    },
    {
      provide: EdcConnectorClient,
      useFactory: (s: AppConfigService) => {
        return new EdcConnectorClient.Builder()
          .federatedCatalogUrl(s.getConfig()?.federatedCatalogApiUrl as string)
          .build();
      },
      deps: [AppConfigService]
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
