import { useState } from 'react'
import './App.css'
import { useConfig } from './config/ConfigContext'
import { useRegistrationApiService, type RegisterParticipantDto } from './api/useRegistrationApiService'

function App() {

  const config = useConfig();
  console.log(config);

  const [did, setDid] = useState("");
  const [connectorDspUrl, setConnectorDspUrl] = useState("");
  const [connectorManagementUrl, setConnectorManagementUrl] = useState("");
  const [connectorApiKey, setConnectorApiKey] = useState("");
  const [identityHubIdentityUrl, setIdentityHubIdentityUrl] = useState("");
  const [identityHubCredentialsUrl, setIdentityHubCredentialsUrl] = useState("");
  const [identityHubApiKey, setIdentityHubApiKey] = useState("");
  const [publicStsKey, setPublicStsKey] = useState("");

  const { registerParticipant } = useRegistrationApiService();

  const setProviderDefaults = () => {
    setDid("did:web:provider-ih%3A7093:bob");
    setConnectorManagementUrl("http://provider-connector:8191/api/management");
    setConnectorDspUrl("http://provider-connector:8192/api/dsp");
    setConnectorApiKey("password");
    setIdentityHubIdentityUrl("http://provider-ih:7092/api/identity");
    setIdentityHubCredentialsUrl("http://provider-ih:7091/api/credentials");
    setIdentityHubApiKey("c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo=");
    setPublicStsKey("-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n");
  }

  const setConsumerDefaults = () => {
    setDid("did:web:consumer-ih%3A7083:alice");
    setConnectorManagementUrl("http://consumer-connector:8081/api/management");
    setConnectorDspUrl("http://consumer-connector:8082/api/dsp");
    setConnectorApiKey("password");
    setIdentityHubIdentityUrl("http://consumer-ih:7082/api/identity");
    setIdentityHubCredentialsUrl("http://consumer-ih:7081/api/credentials");
    setIdentityHubApiKey("c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo=");
    setPublicStsKey("-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n");
  }

  const setFcDefaults = () => {
    setDid("did:web:fc-ih%3A7103:piotr");
    setConnectorManagementUrl("http://federated-catalog:8291/api/management");
    setConnectorDspUrl("http://federated-catalog:8292/api/dsp");
    setConnectorApiKey("password");
    setIdentityHubIdentityUrl("http://fc-ih:7102/api/identity");
    setIdentityHubCredentialsUrl("http://fc-ih:7101/api/credentials");
    setIdentityHubApiKey("c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo=");
    setPublicStsKey("-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----\n");
  }

  const getDataModel = (): RegisterParticipantDto => {
    return {
      connector_did: did,
      connector_dsp_url: connectorDspUrl,
      connector_management_url: connectorManagementUrl,
      connector_api_key: connectorApiKey,
      identity_hub_identity_url: identityHubIdentityUrl,
      identity_hub_credentials_url: identityHubCredentialsUrl,
      identity_hub_api_key: identityHubApiKey,
      sts_public_key_pem: publicStsKey,
      generated_vcs: []
    };
  }

  return (
    <>
      <h1>Participant registration</h1>
      <div style={{ display: "flex", flexDirection: "row"}}>
        <button onClick={setProviderDefaults}>Set Provider Defaults</button>
        <button onClick={setConsumerDefaults}>Set Consumer Defaults</button>
        <button onClick={setFcDefaults}>Set FC Defaults</button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="did">DID</label>
        <input
          id="did"
          type="text"
          value={did}
          onChange={(e) => setDid(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="connectorManagementUrl">Connector Management URL</label>
        <input
          id="connectorManagementUrl"
          type="text"
          value={connectorManagementUrl}
          onChange={(e) => setConnectorManagementUrl(e.target.value)}
        />
      </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="connectorDspUrl">Connector DSP URL</label>
        <input
          id="connectorDspUrl"
          type="text"
          value={connectorDspUrl}
          onChange={(e) => setConnectorDspUrl(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="connectorApiKey">Connector API Key</label>
        <input
          id="connectorApiKey"
          type="text"
          value={connectorApiKey}
          onChange={(e) => setConnectorApiKey(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="identityHubIdentityUrl">Identity Hub Identity URL</label>
        <input
          id="identityHubIdentityUrl"
          type="text"
          value={identityHubIdentityUrl}
          onChange={(e) => setIdentityHubIdentityUrl(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="identityHubCredentialsUrl">Identity Hub Credentials URL</label>
        <input
          id="identityHubCredentialsUrl"
          type="text"
          value={identityHubCredentialsUrl}
          onChange={(e) => setIdentityHubCredentialsUrl(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="identityHubApiKey">Identity Hub API Key</label>
        <input
          id="identityHubApiKey"
          type="text"
          value={identityHubApiKey}
          onChange={(e) => setIdentityHubApiKey(e.target.value)}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <label htmlFor="publicStsKey">Public Sts Key (PEM)</label>
        <input
          id="publicStsKey"
          value={publicStsKey}
          onChange={(e) => setPublicStsKey(e.target.value)}
        />
      </div>
    </div>
      <div className="card">
        <button onClick={() => registerParticipant(getDataModel())}>
          Register
        </button>
      </div>
    </>
  )
}

export default App
