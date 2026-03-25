import type { IssueVcRequest } from "../api/useRegistrationApiService";

export type Service = "provider" | "consumer" | "fc";
export type Env = "local" | "prod";

type Defaults = Record<Env, Record<Service, IssueVcRequest>>;

export const defaults: Defaults = {
  local: {
    provider: {
      connector_did: "did:web:provider-ih%3A7093:bob",
      connector_dsp_url: "http://provider-connector:8192/api/dsp",
      identity_hub_identity_url: "http://provider-ih:7092/api/identity",
      identity_hub_api_key: "c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="
    },
    consumer: {
      connector_did: "did:web:consumer-ih%3A7083:alice",
      connector_dsp_url: "http://consumer-connector:8082/api/dsp",
      identity_hub_identity_url: "http://consumer-ih:7082/api/identity",
      identity_hub_api_key: "c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="
    },
    fc: {
      connector_did: "did:web:fc-ih%3A7103:piotr",
      connector_dsp_url: "http://federated-catalog:8292/api/dsp",
      identity_hub_identity_url: "http://fc-ih:7102/api/identity",
      identity_hub_api_key: "c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="
    }
  },

  prod: {
    provider: {
      connector_did: "did:web:provider-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl:bob",
      connector_dsp_url: "https://provider-connector-dcp-data-space.apps.bst2.paas.psnc.pl/api/dsp",
      identity_hub_identity_url: "https://provider-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/identity",
      identity_hub_api_key: "..."
    },
    consumer: {  
      connector_did: "did:web:consumer-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl:alice",
      connector_dsp_url: "https://consumer-connector-dcp-data-space.apps.bst2.paas.psnc.pl/api/dsp",
      identity_hub_identity_url: "https://consumer-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/identity",
      identity_hub_api_key: "..."
    },
    fc: { 
      connector_did: "did:web:federated-catalog-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl:piotr",
      connector_dsp_url: "https://federated-catalog-dcp-data-space.apps.bst2.paas.psnc.pl/api/dsp",
      identity_hub_identity_url: "https://federated-catalog-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/identity",
      identity_hub_api_key: "..."
    }
  }
};