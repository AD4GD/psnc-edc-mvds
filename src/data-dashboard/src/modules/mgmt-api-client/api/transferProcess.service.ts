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
import { Observable, asyncScheduler, scheduled } from 'rxjs';
import { EdcConnectorClient } from "@think-it-labs/edc-connector-client";
import { TransferProcessState, TransferProcess, TransferProcessInput, QuerySpec, IdResponse } from "../model";



@Injectable({
  providedIn: 'root'
})
export class TransferProcessService {
    private transferProcessService = this.edcConnectorClient.management.transferProcesses;

    constructor(private edcConnectorClient: EdcConnectorClient) {
    }

    /**
     * Requests aborting the transfer process. Due to the asynchronous nature of transfers, a successful response only indicates that the request was successfully received. Clients must poll the /{id}/state endpoint to track the state.
     * @param id
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public cancelTransferProcess(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<any>;
    public cancelTransferProcess(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<any>>;
    public cancelTransferProcess(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<any>>;
    public cancelTransferProcess(id: string): Observable<any> {
        return scheduled(this.transferProcessService.terminate(id, "Call by DataDashboard."), asyncScheduler);
    }

    /**
     * Requests the deprovisioning of resources associated with a transfer process. Due to the asynchronous nature of transfers, a successful response only indicates that the request was successfully received. This may take a long time, so clients must poll the /{id}/state endpoint to track the state.
     * @param id
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public deprovisionTransferProcess(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<any>;
    public deprovisionTransferProcess(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<any>>;
    public deprovisionTransferProcess(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<any>>;
    public deprovisionTransferProcess(id: string): Observable<any> {
      return scheduled(this.transferProcessService.deprovision(id), asyncScheduler)
    }

    /**
     * Gets an transfer process with the given ID
     * @param id
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getTransferProcess(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<TransferProcess>;
    public getTransferProcess(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<TransferProcess>>;
    public getTransferProcess(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<TransferProcess>>;
    public getTransferProcess(id: string): Observable<any> {
        return scheduled(this.transferProcessService.get(id), asyncScheduler)
    }

    /**
     * Gets the state of a transfer process with the given ID
     * @param id
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getTransferProcessState(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<TransferProcessState>;
    public getTransferProcessState(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<TransferProcessState>>;
    public getTransferProcessState(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<TransferProcessState>>;
    public getTransferProcessState(id: string): Observable<any> {
        return scheduled(this.transferProcessService.getState(id), asyncScheduler)
    }

    /**
     * Initiates a data transfer with the given parameters. Please note that successfully invoking this endpoint only means that the transfer was initiated. Clients must poll the /{id}/state endpoint to track the state
     * @param transferRequestInput
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public initiateTransfer(transferRequestInput: TransferProcessInput, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<IdResponse>;
    public initiateTransfer(transferRequestInput: TransferProcessInput, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<IdResponse>>;
    public initiateTransfer(transferRequestInput: TransferProcessInput, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<IdResponse>>;
    public initiateTransfer(transferRequestInput: TransferProcessInput): Observable<any> {
      return scheduled(this.transferProcessService.initiate(transferRequestInput), asyncScheduler)
    }

    /**
     * Returns all transfer process according to a query
     * @param querySpec
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public queryAllTransferProcesses(querySpec?: QuerySpec, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<Array<TransferProcess>>;
    public queryAllTransferProcesses(querySpec?: QuerySpec, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<Array<TransferProcess>>>;
    public queryAllTransferProcesses(querySpec?: QuerySpec, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<Array<TransferProcess>>>;
    public queryAllTransferProcesses(querySpec?: QuerySpec): Observable<any> {
      return scheduled(this.transferProcessService.queryAll(querySpec), asyncScheduler)
    }

}
