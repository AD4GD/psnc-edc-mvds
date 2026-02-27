import { inject } from '@angular/core';
import { CanActivateFn, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
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

export const authGuard: CanActivateFn = async (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {

  const appConfig = inject(AppConfigService);
  if (!appConfig.isOAuthConfigured()) {
    return true;
  }

  const oauthService = inject(OAuthService);
  const router = inject(Router);

  await oauthService.loadDiscoveryDocumentAndTryLogin();

  console.log(oauthService.getAccessToken());
  console.log(oauthService.getIdentityClaims());

  if (oauthService.hasValidAccessToken()) {
    clearUrlFromKeycloakParams();
    
    // Check if there was a stored return URL after successful login
    const returnUrl = sessionStorage.getItem('auth_return_url');
    if (returnUrl) {
      sessionStorage.removeItem('auth_return_url');
      console.log('[Auth] Redirecting to stored URL:', returnUrl);
      await router.navigateByUrl(returnUrl);
      return false; // Prevent navigation to current route, we're redirecting
    }
    
    return true;
  } else {
    // Store the target URL before redirecting to Keycloak
    const targetUrl = state.url;
    console.log('[Auth] Storing return URL:', targetUrl);
    sessionStorage.setItem('auth_return_url', targetUrl);
    
    oauthService.initLoginFlow();
    return false;
  }
};