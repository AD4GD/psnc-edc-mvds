import { PolicyInput } from "@think-it-labs/edc-connector-client";
import { DataService } from "./dataservice";
import { AssetType } from "../enums/asset-type.enum";

export interface CatalogOffer {
    id: string;
    assetId: string;
    properties: any;
    "http://www.w3.org/ns/dcat#dataset": Array<any>;
    "http://www.w3.org/ns/dcat#service": DataService;
    policy: PolicyInput;
    originator: string;
    participantId: string;
    // custom fields
    //
    assetType: AssetType;
    // general optional
    description: string | undefined;
    createdAt: string | undefined;
    updatedAt: string | undefined;
}
