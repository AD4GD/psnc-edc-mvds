import { Catalog } from "@think-it-labs/edc-connector-client";
import { Observable } from 'rxjs';

export interface CatalogApi {
    getAllOffers(): Observable<Catalog[]>
    getOffers(limit: number, offset: number): Observable<Catalog[]>
}
