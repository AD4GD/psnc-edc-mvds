import {HttpClient, HttpErrorResponse, HttpHeaders, HttpParams} from '@angular/common/http';
import {Inject, Injectable} from '@angular/core';
import {EMPTY, from, Observable} from 'rxjs';
import {catchError, map, reduce} from 'rxjs/operators';
import {Catalog} from '../models/catalog';
import {ContractOffer} from '../models/contract-offer';
import {
  ContractNegotiationService,
  TransferProcessService,
} from "../../mgmt-api-client";
import {CONNECTOR_CATALOG_API, CONNECTOR_MANAGEMENT_API} from "../../app/variables";
// import TypeEnum = Policy.TypeEnum; //TODO Use TypeEnum https://github.com/Think-iT-Labs/edc-connector-client/issues/103
import {
  ContractNegotiationRequest,
  ContractNegotiation,
  PolicyInput,
  TransferProcess,
  TransferProcessInput
} from "../../mgmt-api-client/model";
import { EdcConnectorClient } from '@think-it-labs/edc-connector-client';



/**
 * Combines several services that are used from the {@link CatalogBrowserComponent}
 */
@Injectable({
  providedIn: 'root'
})
export class CatalogBrowserService {

  constructor(private httpClient: HttpClient,
              private transferProcessService: TransferProcessService,
              private negotiationService: ContractNegotiationService,
              @Inject(CONNECTOR_MANAGEMENT_API) private managementApiUrl: string,
              @Inject(CONNECTOR_CATALOG_API) private catalogApiUrl: string,
              private edcConnectorClient: EdcConnectorClient) {
  }

  getContractOffers(): Observable<ContractOffer[]> {
    let federatedCatalog = this.edcConnectorClient.federatedCatalog;
    let queryObservable = from(federatedCatalog.queryAll({
      // TODO: add pagination
      limit: 100,
      sortOrder: "DESC"
    }));

    const w3Prefix = "http://www.w3.org/ns/dcat#";
    const edcPrefix = "https://w3id.org/edc/v0.0.1/ns/";
    const odrlPrefix = "http://www.w3.org/ns/odrl/2/";

    return queryObservable
      .pipe(map(catalogs => catalogs.map(catalog => {
        const arr = Array<ContractOffer>();
        let datasets = this.getItemProperties(catalog, "dataset", w3Prefix);
        if (!Array.isArray(datasets)) {
          datasets = [datasets];
        }

        console.log(catalog);
        console.log(datasets);

        for(let i = 0; i < datasets.length; i++) {
          const dataSet: any = datasets[i];
          const properties: { [key: string]: string; } = {
            id: dataSet["@id"],
            type: dataSet["@type"],
            name: this.getItemProperty(dataSet, "name", edcPrefix),
            version: this.getItemProperty(dataSet, "version", edcPrefix),
            contentType: this.getItemProperty(dataSet, "contenttype", edcPrefix),
            proxyPath: this.getItemProperty(dataSet, "proxyPath", edcPrefix),
            proxyQueryParams: this.getItemProperty(dataSet, "proxyQueryParams", edcPrefix),
            baseUrl: this.getItemProperty(dataSet, "baseUrl", edcPrefix),
          }
          const assetId = dataSet["@id"];

          const hasPolicy = this.getFirstPolicy(this.getItemProperty(dataSet, "hasPolicy", odrlPrefix));
          console.log(hasPolicy);

          const policy: PolicyInput = {
            //currently hardcoded to Set since parsed type is {"@policytype": "set"}
            "@type": "Set", //TODO Use TypeEnum https://github.com/Think-iT-Labs/edc-connector-client/issues/103
            "@context" : "http://www.w3.org/ns/odrl.jsonld",
            "uid": hasPolicy["@id"],
            "assignee": hasPolicy["assignee"],
            "assigner": hasPolicy["assigner"],
            "obligation": this.getItemProperty(hasPolicy, "obligation", odrlPrefix),
            "permission": this.getItemProperty(hasPolicy, "permission", odrlPrefix),
            "prohibition": this.getItemProperty(hasPolicy, "prohibition", odrlPrefix),
            "target": this.getItemProperty(hasPolicy, "target", odrlPrefix)
          };

          const newContractOffer: ContractOffer = {
            assetId: assetId,
            properties: properties,
            "http://www.w3.org/ns/dcat#service": this.getItemProperty(catalog, "service", w3Prefix),
            "http://www.w3.org/ns/dcat#dataset": datasets,
            id: hasPolicy["@id"],
            originator: this.getItemProperty(catalog, "originator", edcPrefix),
            policy: policy
          };

          arr.push(newContractOffer)
        }
        return arr;
      })), reduce((acc, val) => {
        for(let i = 0; i < val.length; i++){
          for(let j = 0; j < val[i].length; j++){
            acc.push(val[i][j]);
          }
        }
        return acc;
      }, new Array<ContractOffer>()));
  }

  initiateTransfer(transferRequest: TransferProcessInput): Observable<string> {
    return this.transferProcessService.initiateTransfer(transferRequest).pipe(map(t => t.id!))
  }

  getTransferProcessesById(id: string): Observable<TransferProcess> {
    return this.transferProcessService.getTransferProcess(id);
  }

  initiateNegotiation(initiate: ContractNegotiationRequest): Observable<string> {
    return this.negotiationService.initiateContractNegotiation(initiate).pipe(map(t => t.id!))
  }

  getNegotiationState(id: string): Observable<ContractNegotiation> {
    return this.negotiationService.getNegotiation(id);
  }

  private getFirstPolicy(hasPolicy: any): any {
    if (Array.isArray(hasPolicy)) {
      return hasPolicy[0];
    }
    return hasPolicy;
  }

  private getItemProperties(item: any, property: string, prefix: string): any {
    const field = this.getItemPropertyFullName(property, prefix);
    const fieldValue = item[field];
    return fieldValue;
  }

  private getItemProperty(item: any, property: string, prefix: string): any {
    const field = this.getItemPropertyFullName(property, prefix);
    const fieldValue = item[field];
    
    let result;

    if (Array.isArray(fieldValue)) {
      result = fieldValue[0];
    } else {
      result = fieldValue;
    }

    if (result === undefined || result === null) {
      return result;
    }

    if (result["@value"] !== undefined) {
      return result["@value"];
    }
    return result;
  }

  private getItemPropertyFullName(property: string, prefix: string): string {
    return `${prefix}${property}`;
  }

  private post<T>(urlPath: string,
                  params?: HttpParams | { [param: string]: string | number | boolean | ReadonlyArray<string | number | boolean>; })
    : Observable<T> {
    const url = `${urlPath}`;
    let headers = new HttpHeaders({"Content-type": "application/json"});
    return this.catchError(this.httpClient.post<T>(url, "{\"edc:operandLeft\": \"\",\"edc:operandRight\": \"\",\"edc:operator\": \"\",\"edc:Criterion\":\"\"}", {headers, params}), url, 'POST');
  }

  private catchError<T>(observable: Observable<T>, url: string, method: string): Observable<T> {
    return observable
      .pipe(
        catchError((httpErrorResponse: HttpErrorResponse) => {
          if (httpErrorResponse.error instanceof Error) {
            console.error(`Error accessing URL '${url}', Method: 'GET', Error: '${httpErrorResponse.error.message}'`);
          } else {
            console.error(`Unsuccessful status code accessing URL '${url}', Method: '${method}', StatusCode: '${httpErrorResponse.status}', Error: '${httpErrorResponse.error?.message}'`);
          }

          return EMPTY;
        }));
  }
}
