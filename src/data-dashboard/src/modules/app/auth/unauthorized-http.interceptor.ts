import { Injectable } from '@angular/core';
import {
    HttpErrorResponse,
    HttpEvent,
    HttpHandler,
    HttpInterceptor,
    HttpRequest,
    HttpResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { AppConfigService } from '../app-config.service';
import { AuthSessionService } from './auth-session.service';
import { UnauthorizedScope, UnauthorizedStateService } from './unauthorized-state.service';

@Injectable()
export class UnauthorizedHttpInterceptor implements HttpInterceptor {
    constructor(
        private readonly configService: AppConfigService,
        private readonly unauthorizedState: UnauthorizedStateService,
        private readonly authSession: AuthSessionService
    ) {}

    intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
        const scope = this.resolveScope(req.url);

        return next.handle(req).pipe(
            tap((event) => {
                if (event instanceof HttpResponse) {
                    if (event.status >= 200 && event.status < 300) {
                        this.unauthorizedState.clear(scope);
                    }
                }
            }),
            catchError((err: unknown) => {
                if (err instanceof HttpErrorResponse) {
                    if (err.status === 401) {
                        this.authSession.handleAuthHttpStatus(err.status);
                    }
                    if (err.status === 401 || err.status === 403) {
                        this.unauthorizedState.markUnauthorized(scope);
                    }
                }
                return throwError(() => err);
            })
        );
    }

    private resolveScope(url: string): UnauthorizedScope {
        const config = this.configService.getConfig();

        // If config is not loaded yet, default to management.
        if (!config) {
            return 'management';
        }

        if (url.startsWith(config.catalogUrl)) {
            return 'catalog';
        }

        if (url.startsWith(config.managementApiUrl)) {
            return 'management';
        }

        // Best-effort fallback: catalog endpoints often contain '/catalog' or '/federated' paths,
        // but keep it conservative.
        return 'management';
    }
}
