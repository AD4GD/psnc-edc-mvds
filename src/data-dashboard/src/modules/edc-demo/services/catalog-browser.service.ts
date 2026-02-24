import {HttpClient, HttpErrorResponse, HttpHeaders, HttpParams} from '@angular/common/http';
import {Inject, Injectable} from '@angular/core';
import {asyncScheduler, EMPTY, Observable, scheduled} from 'rxjs';
import {catchError, map, reduce} from 'rxjs/operators';
import {Catalog} from '../models/catalog';
import {ContractOffer} from '../models/contract-offer';
import {
  ContractNegotiationService,
  QUERY_LIMIT,
  TransferProcessService,
} from "../../mgmt-api-client";
import {CONNECTOR_CATALOG_API, CONNECTOR_MANAGEMENT_API} from "../../app/variables";
import { OAuthService } from 'angular-oauth2-oidc';
import { AppConfigService } from '../../app/app-config.service';
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

  constructor(
    private httpClient: HttpClient,
    private transferProcessService: TransferProcessService,
    private negotiationService: ContractNegotiationService,
    @Inject(CONNECTOR_MANAGEMENT_API) private managementApiUrl: string,
    @Inject(CONNECTOR_CATALOG_API) private catalogApiUrl: string,
    private appConfig: AppConfigService,
    private oauthService: OAuthService,
    private edcConnectorClient: EdcConnectorClient
  ) { }

  getContractOffers(): Observable<ContractOffer[]> {
    const querySpec = {
      // TODO: add pagination
      limit: QUERY_LIMIT,
      offset: 0,
      sortOrder: "DESC" as const
    };

    const catalogs$: Observable<any[]> = this.isCatalogProxyUrl(this.catalogApiUrl)
      ? this.httpClient
          .post<any | any[]>(this.catalogApiUrl, querySpec, {
            headers: this.buildCatalogRequestAuthHeaders()
          })
          .pipe(map(c => (Array.isArray(c) ? c : [c])))
      : scheduled(this.edcConnectorClient.federatedCatalog.queryAll(querySpec), asyncScheduler);

    // NOTE: The Federated Catalog returns *compacted* JSON-LD (e.g. keys like "dcat:dataset"
    // and @vocab terms like "name"), not expanded-IRI keys.
    const dcatPrefix = "dcat:";
    const odrlPrefix = "odrl:";
    const dspacePrefix = "dspace:";

    return catalogs$
      .pipe(map(catalogs => catalogs.map(catalog => {
        const arr = Array<ContractOffer>();
        console.log(catalog["dcat:dataset"])
        let datasets = this.getItemProperties(catalog, "dataset", dcatPrefix);
        if (!Array.isArray(datasets)) {
          datasets = [datasets];
        }

        // console.log(catalog);
        // console.log(datasets);

        for(let i = 0; i < datasets.length; i++) {
          const dataSet: any = datasets[i];
          const properties: { [key: string]: string; } = {
            id: dataSet["@id"],
            type: dataSet["@type"],
            // These are @vocab terms in the returned compacted JSON-LD, so they appear unprefixed.
            name: this.getItemProperty(dataSet, "name", ""),
            version: this.getItemProperty(dataSet, "version", ""),
            contentType: this.getItemProperty(dataSet, "contenttype", ""),
            proxyPath: this.getItemProperty(dataSet, "proxyPath", ""),
            proxyQueryParams: this.getItemProperty(dataSet, "proxyQueryParams", ""),
            baseUrl: this.getItemProperty(dataSet, "baseUrl", ""),
          }
          const assetId = dataSet["@id"];

          const hasPolicy = this.getFirstPolicy(this.getItemProperty(dataSet, "hasPolicy", odrlPrefix));
          // console.log(hasPolicy);

          const policy: PolicyInput = {
            //currently hardcoded to Set since parsed type is {"@policytype": "set"}
            "@type": "Set", //TODO Use TypeEnum https://github.com/Think-iT-Labs/edc-connector-client/issues/103
            "@context" : "http://www.w3.org/ns/odrl.jsonld",
            "uid": hasPolicy["@id"],
            "assignee": hasPolicy["assignee"],
            "assigner": hasPolicy["assigner"],
            "obligation": this.getItemProperties(hasPolicy, "obligation", odrlPrefix),
            "permission": this.getItemProperties(hasPolicy, "permission", odrlPrefix),
            "prohibition": this.getItemProperties(hasPolicy, "prohibition", odrlPrefix),
            "target": this.getItemProperty(hasPolicy, "target", odrlPrefix)
          };

          const newContractOffer: ContractOffer = {
            assetId: assetId,
            properties: properties,
            "http://www.w3.org/ns/dcat#service": this.getItemProperty(catalog, "service", dcatPrefix),
            "http://www.w3.org/ns/dcat#dataset": datasets,
            id: hasPolicy["@id"],
            // originator is also an @vocab term in this compacted JSON-LD response.
            originator: this.getItemProperty(catalog, "originator", ""),
            policy: policy,
            participantId: this.getItemProperty(catalog, "participantId", dspacePrefix),
          };

          arr.push(newContractOffer)
        }
        return arr;
      })), reduce((acc, val) => {
        for (let i = 0; i < val.length; i++) {
          for (let j = 0; j < val[i].length; j++) {
            acc.push(val[i][j]);
          }
        }
        return acc;
      }, new Array<ContractOffer>()));
  }

  private isCatalogProxyUrl(url: string | undefined | null): boolean {
    if (url == null) {
      return false;
    }
    // Catalog-proxy endpoint is served under /catalog-proxy/... and ends with /catalog/request.
    return url.includes('/catalog-proxy/') || url.endsWith('/catalog/request');
  }

  private buildCatalogRequestAuthHeaders(): HttpHeaders {
    const config = this.appConfig.getConfig();
    const accessToken = this.oauthService.getAccessToken();

    let headers = new HttpHeaders({ "Content-Type": "application/json" });

    if (accessToken != null && accessToken !== "") {
      headers = headers.set('Authorization', `Bearer ${accessToken}`);
      return headers;
    }

    if (config?.edcApiKey != null && config.edcApiKey !== "") {
      headers = headers.set('X-Api-Key', config.edcApiKey);
    }

    return headers;
  }

  requestDatasetById(counterPartyAddress: string, datasetId: string): Observable<any> {
    const baseUrl = this.managementApiUrl.replace(/\/$/, "");
    const url = `${baseUrl}/v3/catalog/dataset/request`;
    const body = {
      "@context": {
        "edc": "https://w3id.org/edc/v0.0.1/ns/"
      },
      "@type": "CatalogRequest",
      counterPartyAddress: counterPartyAddress,
      "@id": datasetId,
      protocol: "dataspace-protocol-http"
    };

    return this.httpClient.post<any>(url, body, {
      headers: this.buildCatalogRequestAuthHeaders()
    });
  }

  requestDatasetOfferById(counterPartyAddress: string, datasetId: string, participantId: string): Observable<ContractOffer> {
    return this.requestDatasetById(counterPartyAddress, datasetId)
      .pipe(
        map(payload => this.buildContractOfferFromDataset(payload, datasetId, counterPartyAddress, participantId))
      );
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
    const fieldValue = this.getJsonLdField(item, property, prefix);
    return fieldValue;
  }

  private getItemProperty(item: any, property: string, prefix: string): any {
    const fieldValue = this.getJsonLdField(item, property, prefix);
    
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

  private getJsonLdField(item: any, property: string, prefix: string): any {
    if (item == null) {
      return undefined;
    }

    // 1) Try compact form: e.g. "dcat:dataset" or "odrl:hasPolicy"
    if (prefix != null && prefix !== "") {
      const compactKey = `${prefix}${property}`;
      if (Object.prototype.hasOwnProperty.call(item, compactKey)) {
        return item[compactKey];
      }

      // 2) If @context maps the prefix to an IRI, try expanded key too.
      // Example: @context.dcat = "http://www.w3.org/ns/dcat#" -> "http://www.w3.org/ns/dcat#dataset"
      if (prefix.endsWith(":")) {
        const ctx = item["@context"];
        const ctxPrefix = prefix.substring(0, prefix.length - 1);
        const iriBase = ctx != null ? ctx[ctxPrefix] : undefined;
        if (typeof iriBase === "string" && iriBase.length > 0) {
          const expandedKey = `${iriBase}${property}`;
          if (Object.prototype.hasOwnProperty.call(item, expandedKey)) {
            return item[expandedKey];
          }
        }
      }
    }

    // 3) Try @vocab term (unprefixed), e.g. "name", "originator", "proxyPath"
    if (Object.prototype.hasOwnProperty.call(item, property)) {
      return item[property];
    }

    return undefined;
  }

  private buildContractOfferFromDataset(payload: any, datasetId: string, originator: string, participantId: string): ContractOffer {
    const dcatPrefix = "dcat:";
    const odrlPrefix = "odrl:";
    const dspacePrefix = "dspace:";

    const dataset = this.findDatasetInPayload(payload, datasetId);
    if (!dataset) {
      throw new Error(`Dataset ${datasetId} not found in response`);
    }

    const properties: { [key: string]: string } = {
      id: dataset["@id"] ?? datasetId,
      type: dataset["@type"],
      name: this.getItemProperty(dataset, "name", ""),
      version: this.getItemProperty(dataset, "version", ""),
      contentType: this.getItemProperty(dataset, "contenttype", ""),
      proxyPath: this.getItemProperty(dataset, "proxyPath", ""),
      proxyQueryParams: this.getItemProperty(dataset, "proxyQueryParams", ""),
      baseUrl: this.getItemProperty(dataset, "baseUrl", ""),
    };

    const hasPolicy = this.getFirstPolicy(this.getItemProperty(dataset, "hasPolicy", odrlPrefix));

    const policy: PolicyInput = {
      "@type": "Set",
      "@context": "http://www.w3.org/ns/odrl.jsonld",
      "uid": hasPolicy?.["@id"] ?? datasetId,
      "assignee": hasPolicy?.["assignee"],
      "assigner": hasPolicy?.["assigner"],
      "obligation": this.getItemProperties(hasPolicy, "obligation", odrlPrefix),
      "permission": this.getItemProperties(hasPolicy, "permission", odrlPrefix),
      "prohibition": this.getItemProperties(hasPolicy, "prohibition", odrlPrefix),
      "target": this.getItemProperty(hasPolicy, "target", odrlPrefix) ?? datasetId
    };

    const rawDatasets = payload?.["dcat:dataset"] ?? payload?.["http://www.w3.org/ns/dcat#dataset"];
    const datasetList = Array.isArray(rawDatasets)
      ? rawDatasets
      : rawDatasets
        ? [rawDatasets]
        : [dataset];

    return {
      assetId: dataset["@id"] ?? datasetId,
      properties: properties,
      "http://www.w3.org/ns/dcat#service": this.getItemProperty(payload, "service", dcatPrefix),
      "http://www.w3.org/ns/dcat#dataset": datasetList,
      id: hasPolicy?.["@id"] ?? datasetId,
      originator: this.getItemProperty(payload, "originator", "") ?? originator,
      policy: policy,
      participantId: this.getItemProperty(payload, "participantId", dspacePrefix) ?? participantId,
    };
  }

  private findDatasetInPayload(payload: any, datasetId: string): any | null {
    if (!payload) {
      return null;
    }

    const datasetKeys = [
      "dcat:dataset",
      "http://www.w3.org/ns/dcat#dataset",
      "dataset"
    ];

    for (const key of datasetKeys) {
      if (payload[key]) {
        const datasets = Array.isArray(payload[key]) ? payload[key] : [payload[key]];
        const match = datasets.find((_asset: any) => _asset?.["@id"] === datasetId || _asset?.id === datasetId);
        return match ?? datasets[0];
      }
    }

    if (payload["@id"] === datasetId) {
      return payload;
    }

    return null;
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
