import { JsonLdObject } from "@think-it-labs/edc-connector-client";

export interface PolicyRule {
    type: string,
    content: JsonLdObject
}