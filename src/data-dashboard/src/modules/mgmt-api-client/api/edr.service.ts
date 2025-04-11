import { Injectable } from '@angular/core';
import { HttpResponse, HttpEvent, HttpContext } from '@angular/common/http';
import { Observable, asyncScheduler, scheduled } from 'rxjs';
import {EdcConnectorClient} from "@think-it-labs/edc-connector-client";


@Injectable({
  providedIn: 'root'
})
export class EdrService {
    private edrsService = this.edcConnectorClient.management.edrs;

    constructor(private edcConnectorClient: EdcConnectorClient) {
    }

    public requestDataAddress(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<any>;
    public requestDataAddress(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<any>>;
    public requestDataAddress(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<any>>;
    public requestDataAddress(id: string): Observable<any> {
        return scheduled(this.edrsService.dataAddress(id), asyncScheduler);
    }
}
