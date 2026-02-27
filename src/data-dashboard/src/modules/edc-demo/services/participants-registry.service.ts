import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';

interface ParticipantEntry {
    id: string;
    originator: string;
    label?: string;
}

interface ParticipantsRegistry {
    participants: ParticipantEntry[];
}

@Injectable({
    providedIn: 'root'
})
export class ParticipantsRegistryService {
    private readonly registry$ = this.httpClient
    .get<ParticipantsRegistry>('assets/participants.json')
    .pipe(shareReplay(1));

    constructor(private httpClient: HttpClient) {}

    getOriginator(participantId: string): Observable<string | undefined> {
        return this.registry$.pipe(
            map(registry => registry.participants.find(p => p.id === participantId)?.originator)
        );
    }
}
