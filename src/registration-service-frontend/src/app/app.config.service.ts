import { Injectable } from '@angular/core';
import { AuthConfig } from 'angular-oauth2-oidc';

export interface AppConfig {
  registrationServiceApiUrl: string,
  federatedCatalogApiUrl: string,
  environment: string,
  isUseFakeBackend: boolean,
  // present if oauth2.0 is used
  oauthIssuer?: string;
  oauthClientId?: string;
  // present if api key is required by backend, and
  // the website is protected by reverse-proxy with OAuth handling
  edcApiKey?: string;
}

@Injectable({
  providedIn: 'root',
})
export class AppConfigService {
  private config!: AppConfig;
  private authConfig?: AuthConfig;

  constructor() {
  }

  initAuthConfig(config: AppConfig) {
    if (config?.oauthIssuer === undefined || config?.oauthClientId === undefined) {
      return;
    }

    let requireHttps = false;
    if (config.oauthIssuer.includes("https")) {
      requireHttps = true;
    }
    console.log(requireHttps);
    this.authConfig = {
      issuer: config.oauthIssuer,
      clientId: config.oauthClientId,
      redirectUri: window.location.origin,
      responseType: 'code',
      scope: 'openid profile email offline_access',
      showDebugInformation: true,
      sessionChecksEnabled: true,
      strictDiscoveryDocumentValidation: false,
      requireHttps: requireHttps,
      // Enables silent refresh (no full redirects)
      useSilentRefresh: true,
      timeoutFactor: 0.75,
      clearHashAfterLogin: true,
      preserveRequestedRoute: true,
    };
  }

  loadConfig(): Promise<void> {
    return fetch('/assets/config/app.config.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load config.json: ${response.statusText}`);
        }
        return response.json();
      })
      .then((config) => {
        console.log(config);
        this.config = config;
        console.log(this.config);
        this.initAuthConfig(this.config);
      })
      .catch((error) => {
        console.error('Error loading configuration:', error);
      });
  }

  getConfig(): AppConfig {
    console.log(this.config);
    return this.config;
  }

  getOAuthConfig(): AuthConfig | undefined {
    return this.authConfig;
  }

  isOAuthConfigured() {
    return this.getOAuthConfig() !== undefined;
  }
}
