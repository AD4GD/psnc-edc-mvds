import type { RegisterParticipantDto } from "../api/useRegistrationApiService";

export type Service = "provider" | "consumer" | "fc";
export type Env = "local" | "prod";

type Defaults = Record<Env, Record<Service, RegisterParticipantDto>>;

export const defaults: Defaults = {
  local: {
    provider: {
      connector_did: "did:web:provider-ih%3A7093:bob",
      connector_management_url: "http://provider-connector:8191/api/management",
      connector_dsp_url: "http://provider-connector:8192/api/dsp",
      connector_api_key: "password",
      identity_hub_identity_url: "http://provider-ih:7092/api/identity",
      identity_hub_credentials_url: "http://provider-ih:7091/api/credentials",
      identity_hub_api_key: "c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo=",
      sts_public_key_pem: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n",
      generated_vcs: []
    },
    consumer: {
      connector_did: "did:web:consumer-ih%3A7083:alice",
      connector_management_url: "http://consumer-connector:8081/api/management",
      connector_dsp_url: "http://consumer-connector:8082/api/dsp",
      connector_api_key: "password",
      identity_hub_identity_url: "http://consumer-ih:7082/api/identity",
      identity_hub_credentials_url: "http://consumer-ih:7081/api/credentials",
      identity_hub_api_key: "c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo=",
      sts_public_key_pem: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n",
      generated_vcs: []
    },
    fc: {
      connector_did: "did:web:fc-ih%3A7103:piotr",
      connector_management_url: "http://federated-catalog:8291/api/management",
      connector_dsp_url: "http://federated-catalog:8292/api/dsp",
      connector_api_key: "password",
      identity_hub_identity_url: "http://fc-ih:7102/api/identity",
      identity_hub_credentials_url: "http://fc-ih:7101/api/credentials",
      identity_hub_api_key: "c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo=",
      sts_public_key_pem: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n",
      generated_vcs: []
    }
  },

  prod: {
    provider: {
      connector_did: "did:web:provider-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl:bob",
      connector_management_url: "https://provider-connector-dcp-data-space.apps.bst2.paas.psnc.pl/api/management",
      connector_dsp_url: "https://provider-connector-dcp-data-space.apps.bst2.paas.psnc.pl/api/dsp",
      connector_api_key: "password",
      identity_hub_identity_url: "https://provider-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/identity",
      identity_hub_credentials_url: "https://provider-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/credentials",
      identity_hub_api_key: "...",
      sts_public_key_pem: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n",
      generated_vcs: []
    },
    consumer: {  
      connector_did: "did:web:consumer-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl:alice",
      connector_management_url: "https://consumer-connector-dcp-data-space.apps.bst2.paas.psnc.pl/api/management",
      connector_dsp_url: "https://consumer-connector-dcp-data-space.apps.bst2.paas.psnc.pl/api/dsp",
      connector_api_key: "password",
      identity_hub_identity_url: "https://consumer-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/identity",
      identity_hub_credentials_url: "https://consumer-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/credentials",
      identity_hub_api_key: "...",
      sts_public_key_pem: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n",
      generated_vcs: []
    },
    fc: { 
      connector_did: "did:web:federated-catalog-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl:piotr",
      connector_management_url: "https://federated-catalog-dcp-data-space.apps.bst2.paas.psnc.pl/api/management",
      connector_dsp_url: "https://federated-catalog-dcp-data-space.apps.bst2.paas.psnc.pl/api/dsp",
      connector_api_key: "password",
      identity_hub_identity_url: "https://federated-catalog-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/identity",
      identity_hub_credentials_url: "https://federated-catalog-identity-hub-dcp-data-space.apps.bst2.paas.psnc.pl/api/credentials",
      identity_hub_api_key: "...",
      sts_public_key_pem: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n",
      generated_vcs: []
    }
  }
};