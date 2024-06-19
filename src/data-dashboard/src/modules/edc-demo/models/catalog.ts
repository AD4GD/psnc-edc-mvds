import { ContractOffer } from './contract-offer';
import { DataService } from "./data-service";

export interface Catalog {
    id?: string;
    contractOffers?: Array<ContractOffer>;
    "http://www.w3.org/ns/dcat#dataset": Array<any>;
    "http://www.w3.org/ns/dcat#service": DataService;
    "originator": string;
}
