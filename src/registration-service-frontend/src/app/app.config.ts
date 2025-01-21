import { APP_INITIALIZER, ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { ConfigService as AppConfigService } from './core/app.config.service';
import { getBackendApi, getCatalogApi, getClient } from './core/api/services/factories/api-factories';
import { RegistrationServiceClient } from './core/api/services/impl/registration-service-client';
import { EdcConnectorClient } from "@think-it-labs/edc-connector-client";
import { BACKEND_API_TOKEN, CATALOG_API_TOKEN } from './injection-tokens';
import { HttpClient, provideHttpClient } from '@angular/common/http';

export interface AppConfig {
  registrationServiceApiUrl: string,
  federatedCatalogApiUrl: string,
  environment: string,
  isUseFakeBackend: boolean
}

export interface AppConfigEnv {
  REGISTRATION_SERVICE_FRONTEND_BACKEND_URL: string;
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimationsAsync(),
    provideHttpClient(),
    //provideAppInitializer(initializeConfig(new ConfigService())),
    {
      provide: APP_INITIALIZER,
      useFactory: (configService: AppConfigService) => () => configService.loadConfig(),
      deps: [AppConfigService],
      multi: true
    },
    {
      provide: RegistrationServiceClient,
      useFactory: getClient,
      deps: [AppConfigService, EdcConnectorClient, HttpClient]
    },
    {
      provide: CATALOG_API_TOKEN,
      useFactory: getCatalogApi,
      deps: [AppConfigService, EdcConnectorClient]
    },
    {
      provide: BACKEND_API_TOKEN,
      useFactory: getBackendApi,
      deps: [AppConfigService]
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
  ]
};
