import { Inject, Injectable } from "@angular/core";
import { from, map, Observable, of, reduce } from "rxjs";
import { EdcConnectorClient, PolicyInput } from "@think-it-labs/edc-connector-client";
import { DSPACE_PREFIX, EDC_PREFIX, ODRL_PREFIX, W3_PREFIX } from "../common/constants";
import { CatalogOffer } from "../api/models/catalog-offer";
import { CatalogApi } from "../api/services/interfaces/catalog-api.interface";
import { CATALOG_API_TOKEN } from "../../injection-tokens";
import { AssetType } from "../api/enums/asset-type.enum";

@Injectable({
    providedIn: 'root',
})
export class CatalogService {

    constructor(@Inject(CATALOG_API_TOKEN) private catalogApi: CatalogApi) {
    }

    getOffers(limit: number, offset: number, searchTerm: string): Observable<CatalogOffer[]> {
        //let queryObservable = this.catalogApi.getOffers(limit, offset);
        let queryObservable = this.catalogApi.getAllOffers();
        return queryObservable
        .pipe(map(catalogs => catalogs.map(catalog => {
            const arr = Array<CatalogOffer>();

            let datasets = catalog.datasets;
            console.log(catalog);
            console.log(datasets);

            for(let i = 0; i < datasets.length; i++) {
              const dataSet: any = datasets[i];
              const properties: { [key: string]: string; } = {
                id: dataSet["@id"],
                type: dataSet["@type"],
                name: this.getItemProperty(dataSet, "name", EDC_PREFIX),
                version: this.getItemProperty(dataSet, "version", EDC_PREFIX),
                contentType: this.getItemProperty(dataSet, "contenttype", EDC_PREFIX),
                proxyPath: this.getItemProperty(dataSet, "proxyPath", EDC_PREFIX),
                proxyQueryParams: this.getItemProperty(dataSet, "proxyQueryParams", EDC_PREFIX),
                baseUrl: this.getItemProperty(dataSet, "baseUrl", EDC_PREFIX),
              }
              const assetId = dataSet["@id"];

              const hasPolicy = this.getFirstPolicy(this.getItemProperty(dataSet, "hasPolicy", ODRL_PREFIX));

              const policy: PolicyInput = {
                "@type": "Set",
                "@context" : "http://www.w3.org/ns/odrl.jsonld",
                "uid": hasPolicy["@id"],
                "assignee": hasPolicy["assignee"],
                "assigner": hasPolicy["assigner"],
                "obligation": this.getItemProperties(hasPolicy, "obligation", ODRL_PREFIX),
                "permission": this.getItemProperties(hasPolicy, "permission", ODRL_PREFIX),
                "prohibition": this.getItemProperties(hasPolicy, "prohibition", ODRL_PREFIX),
                "target": this.getItemProperty(hasPolicy, "target", ODRL_PREFIX)
              };

              const newContractOffer: CatalogOffer = {
                assetId: assetId,
                properties: properties,
                "http://www.w3.org/ns/dcat#service": this.getItemProperty(catalog, "service", W3_PREFIX),
                "http://www.w3.org/ns/dcat#dataset": datasets,
                id: hasPolicy["@id"],
                originator: this.getItemProperty(catalog, "originator", EDC_PREFIX),
                policy: policy,
                participantId: this.getItemProperty(catalog, "participantId", DSPACE_PREFIX),
                assetType: AssetType.HttpData,
                description: undefined,
                createdAt: undefined,
                updatedAt: undefined
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

             // custom filtering
            if (searchTerm !== "" && searchTerm !== undefined) {
              acc = acc.filter(x =>
                x.properties.name.toLowerCase().includes(searchTerm) ||
                x.assetId.toLowerCase().includes(searchTerm))
            }

            // custom pagination
            if (limit != 0) {
              const from = offset;
              const to = from + limit;
              acc = acc.filter((x, index) => index >= from && index < to);
            }

            return acc;
          }, new Array<CatalogOffer>()));
    }

    getLength(searchTerm: string): Observable<number> {
      // (0, 0) - get all offers
      return this.getOffers(0, 0, searchTerm).pipe(map(offers => offers.length));
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
}
