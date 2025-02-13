import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { OAuthService } from 'angular-oauth2-oidc';
import { AppConfigService } from '../app-config.service';

const clearUrlFromKeycloakParams = () => {
  setTimeout(() => {
    const href = window.location.href
      .replace(/[&?]code=[^&$]*/, '')
      .replace(/[&?]scope=[^&$]*/, '')
      .replace(/[&?]state=[^&$]*/, '')
      .replace(/[&?]iss=[^&$]*/, '')
      .replace(/[&?]session_state=[^&$]*/, '');
    history.replaceState(null, window.name, href);
  }, 100);
}

export const authGuard: CanActivateFn = async () => {

  const appConfig = inject(AppConfigService);
  if (!appConfig.isOAuthConfigured()) {
    return true;
  }

  const oauthService = inject(OAuthService);

  await oauthService.loadDiscoveryDocumentAndTryLogin();

  console.log(oauthService.getAccessToken());
  console.log(oauthService.getIdentityClaims());

  if (oauthService.hasValidAccessToken()) {
    clearUrlFromKeycloakParams();
    return true;
  } else {
    oauthService.initLoginFlow();
    return false;
  }
};