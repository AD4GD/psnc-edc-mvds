import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable, of, shareReplay, switchMap } from 'rxjs';
import { AppConfigService } from '../../app/app-config.service';

interface ParticipantEntry {
    id: string;
    originator: string;
    label?: string;
}

interface FederatedCatalogTarget {
    name: string;
    id: string;
    url: string;
    supportedProtocols: string[];
}

@Injectable({
    providedIn: 'root'
})
export class ParticipantsRegistryService {
    private readonly registry$ = of(null).pipe(
        switchMap(() => {
            const config = this.appConfigService.getConfig();
            if (!config?.federatedCatalogUrl) {
                console.warn('Federated Catalog URL not configured');
                return of([]);
            }
            return this.httpClient
                .get<FederatedCatalogTarget[]>(`${config.federatedCatalogUrl}/api/targets/v1/targets`)
                .pipe(
                    map(targets => this.mapTargetsToParticipants(targets))
                );
        }),
        shareReplay(1)
    );

    constructor(
        private httpClient: HttpClient,
        private appConfigService: AppConfigService
    ) {}

    private mapTargetsToParticipants(targets: FederatedCatalogTarget[]): ParticipantEntry[] {
        return targets.map(target => ({
            id: target.id,
            originator: target.url,
            label: target.name
        }));
    }

    getOriginator(participantId: string): Observable<string | undefined> {
        return this.registry$.pipe(
            map(participants => participants.find(p => p.id === participantId)?.originator)
        );
    }
}
