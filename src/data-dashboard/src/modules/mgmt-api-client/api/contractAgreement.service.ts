/**
 * EDC REST API
 * EDC REST APIs - merged by OpenApiMerger
 *
 * The version of the OpenAPI document: 0.0.1-SNAPSHOT
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
/* tslint:disable:no-unused-variable member-ordering */

import { Injectable } from '@angular/core';
import { HttpResponse, HttpEvent, HttpContext } from '@angular/common/http';
import { Observable, scheduled, asyncScheduler } from 'rxjs';

import { EdcConnectorClient } from '@think-it-labs/edc-connector-client';
import { ContractAgreement, QuerySpec } from '../model'


@Injectable({
  providedIn: 'root'
})
export class ContractAgreementService {

    private contractAgreements = this.edcConnectorClient.management.contractAgreements;

    constructor(private edcConnectorClient: EdcConnectorClient) {

    }

    /**
     * Gets all contract agreements according to a particular query
     * @param querySpec
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public queryAllAgreements(querySpec?: QuerySpec, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<Array<ContractAgreement>>;
    public queryAllAgreements(querySpec?: QuerySpec, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<Array<ContractAgreement>>>;
    public queryAllAgreements(querySpec?: QuerySpec, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<Array<ContractAgreement>>>;
    public queryAllAgreements(querySpec?: QuerySpec): Observable<any> {
        return scheduled(this.contractAgreements.queryAll(querySpec), asyncScheduler)
    }

}
