import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import { LocationStrategy } from '@angular/common';
import { AuthConfig } from 'angular-oauth2-oidc';

export interface AppConfig {
  managementApiUrl: string;
  catalogUrl: string;
  storageAccount: string;
  storageExplorerLinkTemplate: string;
  theme: string;
  backendUrl?: string;
  // present if oauth2.0 is used
  oauthIssuer?: string;
  oauthClientId?: string;
  // present if api key is required by backend, and 
  // the website is protected by reverse-proxy with OAuth handling
  edcApiKey?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AppConfigService {
  config?: AppConfig;
  authConfig?: AuthConfig;

  constructor(private http: HttpClient, private locationStrategy: LocationStrategy) {}

  loadConfig(): Promise<void> {
    let appConfigUrl = this.locationStrategy.prepareExternalUrl('assets/config/app.config.json');

    return this.http
      .get<AppConfig>(appConfigUrl)
      .toPromise()
      .then(data => {
        this.config = data;
        if (data?.oauthIssuer !== undefined && data?.oauthClientId !== undefined) {
          let requireHttps = false;
          if (data.oauthIssuer.includes("https")) {
            requireHttps = true;
          }
          console.log(requireHttps);
          this.authConfig = {
            issuer: data.oauthIssuer,
            clientId: data.oauthClientId,
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
      });
  }

  getConfig(): AppConfig | undefined {
    return this.config;
  }

  getOAuthConfig(): AuthConfig | undefined {
    return this.authConfig;
  }

  isOAuthConfigured() {
    return this.getOAuthConfig() !== undefined;
  }
}
