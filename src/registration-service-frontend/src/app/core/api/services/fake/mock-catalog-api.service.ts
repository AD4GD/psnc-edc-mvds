import { Injectable } from "@angular/core";
import { from, Observable, of } from "rxjs";
import { Catalog } from "@think-it-labs/edc-connector-client";
import { CatalogApi } from "../interfaces/catalog-api.interface";

@Injectable({
    providedIn: 'root',
  })
  export class MockCatalogApiService implements CatalogApi {
    getOffers(limit: number, offset: number): Observable<Catalog[]> {
      return from(fetch('/assets/mocks/mock-fc-response.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load mock response: ${response.statusText}`);
        }
        return response.json();
      })
      .then((result) => {
        return result;
      })
      .catch((error) => {
        console.error('Error loading configuration:', error);
      }));
    }

    getAllOffers() {
      return this.getOffers(0, 0);
  }
}
