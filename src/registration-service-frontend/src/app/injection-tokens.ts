import { InjectionToken } from "@angular/core";
import { CatalogApi } from "./core/api/services/interfaces/catalog-api.interface";
import { BackendApi } from "./core/api/services/interfaces/backend-api.interface";

export const CATALOG_API_TOKEN = new InjectionToken<CatalogApi>('CatalogApi');
export const BACKEND_API_TOKEN = new InjectionToken<BackendApi>('BackendApi');
