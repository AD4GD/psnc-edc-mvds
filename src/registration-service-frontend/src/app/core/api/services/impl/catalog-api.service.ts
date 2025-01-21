import { Injectable } from "@angular/core";
import { from, Observable } from "rxjs";
import { CatalogApi } from "../interfaces/catalog-api.interface";
import { Catalog, EdcConnectorClient } from "@think-it-labs/edc-connector-client";

@Injectable({
    providedIn: 'root',
})
export class CatalogApiService implements CatalogApi {

    constructor(private edcClient: EdcConnectorClient) {
    }

    getOffers(limit: number, offset: number): Observable<Catalog[]> {
        let federatedCatalog = this.edcClient.federatedCatalog;
        let queryObservable = from(federatedCatalog.queryAll({
            limit: limit == 0 ? undefined : limit,
            offset: limit == 0 ? undefined : offset,
            sortOrder: "DESC"
        }));

        return queryObservable;
    }

    getAllOffers(): Observable<Catalog[]> {
        let federatedCatalog = this.edcClient.federatedCatalog;
        let queryObservable = from(federatedCatalog.queryAll({
            sortOrder: "DESC"
        }));

        return queryObservable;
    }
}
