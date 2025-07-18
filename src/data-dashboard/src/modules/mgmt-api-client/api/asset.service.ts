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

import { EdcConnectorClient } from '@think-it-labs/edc-connector-client';
import { AssetInput, Asset, IdResponse, QuerySpec } from "../model"

@Injectable({
  providedIn: 'root'
})
export class AssetService {

    private assets = this.edcConnectorClient.management.assets;

    constructor(private edcConnectorClient: EdcConnectorClient) {
    }

    /**
     * Creates a new asset together with a data address
     * @param assetEntryDto
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public createAsset(assetEntryDto: AssetInput, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<IdResponse>;
    public createAsset(assetEntryDto: AssetInput, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<IdResponse>>;
    public createAsset(assetEntryDto: AssetInput, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<IdResponse>>;
    public createAsset(assetEntryDto: AssetInput): Observable<any> {
        return scheduled(this.assets.create(assetEntryDto), asyncScheduler)
    }

    /**
     * Gets an asset with the given ID
     * @param id
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getAsset(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<Asset>;
    public getAsset(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<Asset>>;
    public getAsset(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<Asset>>;
    public getAsset(id: string): Observable<any> {
        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling getAsset.');
        }

        return scheduled(this.assets.get(id), asyncScheduler)

    }

    /**
     * Removes an asset with the given ID if possible. Deleting an asset is only possible if that asset is not yet referenced by a contract agreement, in which case an error is returned. DANGER ZONE: Note that deleting assets can have unexpected results, especially for contract offers that have been sent out or ongoing or contract negotiations.
     * @param id
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public removeAsset(id: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<any>;
    public removeAsset(id: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<any>>;
    public removeAsset(id: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<any>>;
    public removeAsset(id: string): Observable<any> {
        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling removeAsset.');
        }

        return scheduled(this.assets.delete(id), asyncScheduler)
    }

    /**
     *  all assets according to a particular query
     * @param querySpec
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public requestAssets(querySpec?: QuerySpec, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<Array<Asset>>;
    public requestAssets(querySpec?: QuerySpec, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpResponse<Array<Asset>>>;
    public requestAssets(querySpec?: QuerySpec, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext}): Observable<HttpEvent<Array<Asset>>>;
    public requestAssets(querySpec?: QuerySpec): Observable<any> {
        return scheduled(this.assets.queryAll(querySpec), asyncScheduler)
    }

}
