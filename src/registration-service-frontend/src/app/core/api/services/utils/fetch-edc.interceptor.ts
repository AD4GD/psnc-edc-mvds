import { Injectable } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { AppConfig, AppConfigService } from '../../../../app.config.service';

/*
we need to use this service as a workaround,
since EDC ts client library uses fetch for all requests,
and they doesn't provide a feature to include custom headers such as Authorization header
*/
@Injectable({
  providedIn: 'root',
})
export class FetchInterceptorService {
  constructor(
    private appConfig: AppConfigService,
    private oauthService: OAuthService
  ) {}

  isBackendUrl = (url: string, config: AppConfig) => {
    return url.startsWith(config.federatedCatalogApiUrl);
  };

  convertInputToUrlString = (input: RequestInfo | URL) => {
    let url = "";
    if (input instanceof Request) {
      url = input.url;
    } else if (input instanceof URL) {
      url = input.toString();
    } else {
      url = input;
    }
    return url;
  }

  isNoAuthConfigured = (accessToken: string, config: AppConfig) => {
    return (accessToken == null || accessToken === "") &&
           (config.edcApiKey == null || config.edcApiKey === "");
  }

  cloneHeadersAndAddAuth = (accessToken: string, url: string, config: AppConfig, init?: RequestInit): RequestInit => {
    console.log('Intercepting fetch request:', url);

    let modifiedInit: RequestInit = { ...init };

    const modifiedHeaders = new Headers(modifiedInit?.headers || {});

    const originalContentType = init?.headers instanceof Headers
    ? init.headers.get('Content-Type')
    : init?.headers && 'Content-Type' in init.headers
        ? (init.headers as Record<string, string>)['Content-Type']
        : null;

    if (originalContentType) {
        modifiedHeaders.set('Content-Type', originalContentType);
    } else {
        modifiedHeaders.set('Content-Type', 'application/json');
    }

    if (accessToken) {
        modifiedHeaders.set('Authorization', `Bearer ${accessToken}`);
    } else {
        modifiedHeaders.set('X-Api-Key', config.edcApiKey ?? '');
    }

    modifiedInit.headers = modifiedHeaders;
    return modifiedInit;
  }

  initFetchInterceptor(): void {
    const originalFetch = window.fetch;

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {

      const config = this.appConfig.getConfig();
      if (!config) {
        console.warn('AppConfigService config is undefined.');
        return originalFetch(input, init);
      }

      let url = this.convertInputToUrlString(input);

      if (!this.isBackendUrl(url, config)) {
        return originalFetch(input, init);
      }

      const accessToken = this.oauthService.getAccessToken();
      console.log(accessToken);

      if (this.isNoAuthConfigured(accessToken, config)) {
        // assume that there's no authentication, all endpoints are public
        return originalFetch(input, init);
      }

      const modifiedInit = this.cloneHeadersAndAddAuth(accessToken, url, config, init);

      return originalFetch(input, modifiedInit);
    };
  }
}
