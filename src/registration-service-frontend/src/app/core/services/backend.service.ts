import { Inject, Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { BACKEND_API_TOKEN } from "../../injection-tokens";
import { BackendApi } from "../api/services/interfaces/backend-api.interface";
import { Participant } from "../api/models/participant";
import { ParticipantStatusType } from "../api/enums/participant-status-type.enum";
import { HttpResponse } from "@angular/common/http";

@Injectable({
    providedIn: 'root',
})
export class BackendService {

    constructor(@Inject(BACKEND_API_TOKEN) private backendApi: BackendApi) {
    }

    getParticipants(): Observable<Participant[]> {
      return this.backendApi.getParticipants();
    }

    updateParticipantStatus(did: string, status: ParticipantStatusType): Observable<HttpResponse<any>> {
      return this.backendApi.updateParticipantStatus(did, status);
    }

    updateParticipantClaims(did: string, claims: Map<string, string>): Observable<HttpResponse<any>> {
      return this.backendApi.updateParticipantClaims(did, claims)
    }

    addParticipant(did: string, protocolUrl: string): Observable<HttpResponse<any>> {
      return this.backendApi.addParticipant(did, protocolUrl);
    }

    deleteParticipant(did: string): Observable<HttpResponse<any>> {
      return this.backendApi.deleteParticipant(did);
    }
}
