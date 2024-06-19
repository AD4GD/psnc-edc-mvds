import {DataService} from "./data-service";
import {PolicyInput} from "../../mgmt-api-client/model";

export interface ContractOffer {
  id: string;
  assetId: string;
  properties: any;
  "http://www.w3.org/ns/dcat#dataset": Array<any>;
  "http://www.w3.org/ns/dcat#service": DataService;
  policy: PolicyInput;
  originator: string;
}
