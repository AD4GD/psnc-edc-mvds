import { Injectable } from '@angular/core';
import { OAuthService, OAuthEvent } from 'angular-oauth2-oidc';
import { filter } from 'rxjs/operators';
import { AppConfigService } from '../app-config.service';
import { UnauthorizedStateService } from './unauthorized-state.service';

@Injectable({
    providedIn: 'root',
})
export class AuthSessionService {
    private actionTimer?: ReturnType<typeof setTimeout>;
    private refreshInFlight?: Promise<boolean>;
    private readonly expirySkewMs = 1_000;
    private initialized = false;

    constructor(
        private readonly oauthService: OAuthService,
        private readonly appConfig: AppConfigService,
        private readonly unauthorizedState: UnauthorizedStateService
    ) {}

    /**
        * Starts monitoring token lifetime. When the access token expires, tries to refresh it using refresh_token;
        * logs out only if refresh fails.
    * Safe to call multiple times.
    */
    init(): void {
        if (this.initialized) {
            return;
        }
        this.initialized = true;

        // Schedule based on current token (if any)
        this.scheduleActionAtExpiry();

        // Reschedule whenever a new token arrives
        this.oauthService.events
        .pipe(filter((e: OAuthEvent) => e.type === 'token_received'))
        .subscribe(() => this.scheduleActionAtExpiry());

        // If refresh/token validation fails, force logout (prevents stuck UI with invalid token)
        this.oauthService.events
        .pipe(
            filter((e: OAuthEvent) =>
                ['token_refresh_error', 'token_validation_error', 'token_error', 'session_error'].includes(e.type)
            )
        )
        .subscribe(() => this.logoutDueToInvalidSession());
    }

    /**
     * Call this when you see a 401/403. If token is expired/invalid, logs out.
     */
    handleAuthHttpStatus(status: number): void {
        if (!this.appConfig.isOAuthConfigured()) {
            return;
        }

        if (status !== 401) {
            return;
        }

        const accessToken = this.oauthService.getAccessToken();
        if (!accessToken) {
        // OAuth is enabled but we have no token; force re-auth.
        this.logoutDueToInvalidSession();
            return;
        }

        // Distinguish "expired/invalid token" from "valid token but no permissions".
        // Backend may still return 401 for authorization failures, so we only logout when token is actually expired.
        const expMs = this.getJwtExpMs(accessToken);
        if (expMs != null) {
            if (expMs <= Date.now() + this.expirySkewMs) {
                // Token is expired: attempt refresh before logging out.
                void this.tryRefreshOrLogout();
            }
            return;
        }

        // Fallback if we can't parse exp
        if (!this.oauthService.hasValidAccessToken()) {
            void this.tryRefreshOrLogout();
        }
    }

    logout(): void {
        this.clearActionTimer();
        this.unauthorizedState.clearAll();
        this.oauthService.logOut();
    }

    private logoutDueToInvalidSession(): void {
        this.clearActionTimer();
        this.unauthorizedState.clearAll();
        this.oauthService.logOut();
    }

    private scheduleActionAtExpiry(): void {
        this.clearActionTimer();

        const accessToken = this.oauthService.getAccessToken();
        if (!accessToken) {
            return;
        }

        const expirationMs = this.getJwtExpMs(accessToken) ?? this.oauthService.getAccessTokenExpiration();
        if (!expirationMs || Number.isNaN(expirationMs)) {
            return;
        }

        const now = Date.now();
        const delay = Math.max(0, expirationMs - now);

        // When access token expires, try to refresh it using refresh_token.
        // We add a small skew so we act *after* expiry, per backend semantics.
        this.actionTimer = setTimeout(() => {
            void this.tryRefreshOrLogout();
        }, delay + this.expirySkewMs);
    }

    private async tryRefreshOrLogout(): Promise<void> {
        // If refresh token flow is disabled (or OAuth is not ready), fall back to logout.
        if (!this.appConfig.isOAuthConfigured()) {
            this.logoutDueToInvalidSession();
            return;
        }

        const refreshed = await this.tryRefreshToken();
        if (!refreshed) {
            this.logoutDueToInvalidSession();
            return;
        }

        // Refresh succeeded: schedule next expiry action.
        this.scheduleActionAtExpiry();
    }

    private async tryRefreshToken(): Promise<boolean> {
        if (this.refreshInFlight) {
            return this.refreshInFlight;
        }

        this.refreshInFlight = (async () => {
            try {
                // Ensure we know the token endpoint before attempting refresh.
                // (If the guard hasn't loaded the discovery document yet, refreshToken() would fail.)
                const tokenEndpoint = (this.oauthService as any).tokenEndpoint as string | undefined;
                if (!tokenEndpoint) {
                    await this.oauthService.loadDiscoveryDocument();
                }

                // angular-oauth2-oidc will use the refresh_token grant when configured and a refresh token exists.
                await this.oauthService.refreshToken();
                return this.oauthService.hasValidAccessToken();
            } catch {
                return false;
            } finally {
                this.refreshInFlight = undefined;
            }
        })();

        return this.refreshInFlight;
    }

    private getJwtExpMs(token: string): number | null {
        try {
            const parts = token.split('.');
            if (parts.length < 2) {
                return null;
            }

            const payload = parts[1]
            .replace(/-/g, '+')
            .replace(/_/g, '/');

            // Add padding if needed
            const padded = payload + '='.repeat((4 - (payload.length % 4)) % 4);
            const json = JSON.parse(atob(padded));
            const exp = typeof json?.exp === 'number' ? json.exp : null;
            return exp != null ? exp * 1000 : null;
        } catch {
            return null;
        }
    }

    private clearActionTimer(): void {
        if (this.actionTimer) {
            clearTimeout(this.actionTimer);
            this.actionTimer = undefined;
        }
    }
}
