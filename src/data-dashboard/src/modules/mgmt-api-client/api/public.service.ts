import { Injectable }                      from '@angular/core';
import { HttpResponse, HttpEvent, HttpContext }              from '@angular/common/http';
import { Observable, from }                                        from 'rxjs';
import {EdcConnectorClient, EdcConnectorClientContext} from "@think-it-labs/edc-connector-client";



@Injectable({
  providedIn: 'root'
})
export class PublicService {
    private publicService = this.edcConnectorClient.public;

    constructor(private edcConnectorClient: EdcConnectorClient) {
    }

    public getTransferredData(authCode: string, context: EdcConnectorClientContext, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<any>;
    public getTransferredData(authCode: string, context: EdcConnectorClientContext, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<any>>;
    public getTransferredData(authCode: string, context: EdcConnectorClientContext, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<any>>;
    public getTransferredData(authCode: string, context: EdcConnectorClientContext): Observable<any> {
        const headers: Record<string, string | undefined> = {
          "Authorization": authCode
        };
        const url = context.public;

        return from(this.transferData(url, headers));
    }

    // fixed method, original .getTransferredData doesn't work correctly
    // since it doesn't allow to pass parameters
    private transferData(url: string, headers: any): Promise<Response> {
      return fetch(url, {
        method: 'GET',
        headers: headers
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response;
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        throw error;
      });
    }
}
