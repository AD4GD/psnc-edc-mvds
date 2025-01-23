import { Observable } from 'rxjs';
import { Participant } from "../../models/participant";
import { ParticipantStatusType } from '../../enums/participant-status-type.enum';
import { HttpResponse } from '@angular/common/http';

export interface BackendApi {
    getParticipants(): Observable<Participant[]>
    updateParticipantStatus(did: string, status: ParticipantStatusType): Observable<HttpResponse<any>>
    updateParticipantClaims(did: string, claims: Map<string, string>): Observable<HttpResponse<any>>
    addParticipant(did: string, protocolUrl: string): Observable<HttpResponse<any>>
    deleteParticipant(did: string): Observable<HttpResponse<any>>
}
