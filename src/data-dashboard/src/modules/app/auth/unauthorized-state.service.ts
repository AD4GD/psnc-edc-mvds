import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { distinctUntilChanged, map } from 'rxjs/operators';

export type UnauthorizedScope = 'management' | 'catalog';

type UnauthorizedState = Record<UnauthorizedScope, boolean>;

@Injectable({
    providedIn: 'root',
})
export class UnauthorizedStateService {
    private readonly state$ = new BehaviorSubject<UnauthorizedState>({
        management: false,
        catalog: false,
    });

    isUnauthorized$(scope: UnauthorizedScope): Observable<boolean> {
        return this.state$.pipe(
            map((s) => s[scope]),
            distinctUntilChanged()
        );
    }

    isUnauthorized(scope: UnauthorizedScope): boolean {
        return this.state$.value[scope];
    }

    markUnauthorized(scope: UnauthorizedScope): void {
        const current = this.state$.value;
        if (current[scope]) {
            return;
        }
        this.state$.next({ ...current, [scope]: true });
    }

    clear(scope: UnauthorizedScope): void {
        const current = this.state$.value;
        if (!current[scope]) {
            return;
        }
        this.state$.next({ ...current, [scope]: false });
    }

    clearAll(): void {
        this.state$.next({ management: false, catalog: false });
    }
}
