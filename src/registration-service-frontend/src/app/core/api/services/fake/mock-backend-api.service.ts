import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { BackendApi } from "../interfaces/backend-api.interface";
import { Participant } from "../../models/participant";
import { ParticipantStatusType } from "../../enums/participant-status-type.enum";
import { HttpResponse } from "@angular/common/http";

@Injectable({
    providedIn: 'root',
  })
  export class MockBackendApiService implements BackendApi {

    getParticipants(): Observable<Participant[]> {
      return of([
      ]);
    }

    updateParticipantStatus(did: string, status: ParticipantStatusType): Observable<HttpResponse<any>> {
      return of(new HttpResponse());
    }

    updateParticipantClaims(did: string, claims: Map<string, string>): Observable<HttpResponse<any>> {
      return of(new HttpResponse());
    }

    addParticipant(did: string, protocolUrl: string): Observable<HttpResponse<any>> {
      return of(new HttpResponse());
    }

    deleteParticipant(did: string): Observable<HttpResponse<any>> {
      return of(new HttpResponse());
    }
}
