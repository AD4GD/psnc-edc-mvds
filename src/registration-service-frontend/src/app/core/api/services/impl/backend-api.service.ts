import { Injectable } from "@angular/core";
import { ConfigService } from "../../../app.config.service";
import { HttpClient, HttpResponse } from "@angular/common/http";
import { BackendApi } from "../interfaces/backend-api.interface";
import { Participant } from "../../models/participant";
import { Observable } from "rxjs";
import { ParticipantStatusType } from "../../enums/participant-status-type.enum";

@Injectable({
    providedIn: 'root',
})
export class BackendApiService implements BackendApi {

    private PARTICIPANTS_ENDPOINT: string = "authority/registry/participants";
    private CLAIMS_ENDPOINT: string = "claims";

    private apiUrl: string;


    constructor(
        private configService: ConfigService,
        private http: HttpClient
    ) {
        this.apiUrl = this.configService.getConfig().registrationServiceApiUrl;
    }

    getParticipants() {
        return this.http.get<Participant[]>(
            `${this.apiUrl}/${this.PARTICIPANTS_ENDPOINT}`
        );
    }

    updateParticipantStatus(did: string, status: ParticipantStatusType): Observable<HttpResponse<any>> {
        return this.http.patch<HttpResponse<any>>(
            `${this.apiUrl}/${this.PARTICIPANTS_ENDPOINT}/${did}?status=${status}`, {}, { observe: 'response' }
        );
    }

    updateParticipantClaims(did: string, claims: Map<string, string>): Observable<HttpResponse<any>> {
        const claimsObject = Object.fromEntries(claims);
        return this.http.patch<HttpResponse<any>>(
            `${this.apiUrl}/${this.PARTICIPANTS_ENDPOINT}/${did}/${this.CLAIMS_ENDPOINT}`, claimsObject, { observe: 'response' }
        );
    }

    addParticipant(did: string, protocolUrl: string): Observable<HttpResponse<any>> {
        return this.http.post(
            `${this.apiUrl}/${this.PARTICIPANTS_ENDPOINT}?did=${did}&protocolUrl=${protocolUrl}`, {}, { observe: 'response' }
        );
    }

    deleteParticipant(did: string): Observable<HttpResponse<any>> {
        return this.http.delete(
            `${this.apiUrl}/${this.PARTICIPANTS_ENDPOINT}/${did}`, { observe: 'response' }
        );
    }
}
