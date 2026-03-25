import { useState } from 'react'
import './App.css'
import { useConfig } from './config/ConfigContext'
import { useRegistrationApiService, type IssueVcRequest } from './api/useRegistrationApiService'
import { defaults, type Env, type Service } from "./config/defaults";

type FormState = IssueVcRequest;

const emptyForm: FormState = {
  connector_did: "",
  connector_dsp_url: "",
  identity_hub_identity_url: "",
  identity_hub_api_key: ""
};

const envFromConfig = (isProduction: boolean): Env => (isProduction ? "prod" : "local");

function App() {
  const config = useConfig();
  const env = envFromConfig(config.isProduction); // <- runtime config approach

  const setServiceDefaults = (svc: Service) => {
    setForm(defaults[env][svc]);
  };

  const [form, setForm] = useState<FormState>(emptyForm);

  console.log(config);

  const { issueVc } = useRegistrationApiService();

  const setProviderDefaults = () => {
    setServiceDefaults("provider");
  }

  const setConsumerDefaults = () => {
    setServiceDefaults("consumer");
  }

  const setFcDefaults = () => {
    setServiceDefaults("fc");
  }

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  function Field(props: {
    label: string;
    value: string;
    onChange: (v: string) => void;
  }) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <label>{props.label}</label>
        <input
          value={props.value}
          onChange={(e) => props.onChange(e.target.value)}
        />
      </div>
    );
  }

  return (
    <>
      <h1>Verifiable Credentials Issuance</h1>
      <div style={{ display: "flex", flexDirection: "row"}}>
        <button onClick={setProviderDefaults}>Set Provider Defaults</button>
        <button onClick={setConsumerDefaults}>Set Consumer Defaults</button>
        <button onClick={setFcDefaults}>Set FC Defaults</button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 16 }}>
        <Field label="DID" value={form.connector_did} onChange={(v) => update("connector_did", v)} />
        <Field label="Connector DSP URL" value={form.connector_dsp_url} onChange={(v) => update("connector_dsp_url", v)} />
        <Field label="Identity Hub Identity URL" value={form.identity_hub_identity_url} onChange={(v) => update("identity_hub_identity_url", v)} />
        <Field label="Identity Hub API Key" value={form.identity_hub_api_key} onChange={(v) => update("identity_hub_api_key", v)} />
      </div>

      <div className="card">
        <button onClick={() => issueVc(form)}>
          Issue VCs
        </button>
      </div>
    </>
  )
}

export default App
