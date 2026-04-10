import { useState } from "react";
import { useApi } from "../api/apiClient";
import { useAuth } from "../auth/AuthContext";

interface VcForm {
  connector_did: string;
  connector_dsp_url: string;
  identity_hub_identity_url: string;
  identity_hub_api_key: string;
}

const emptyForm: VcForm = {
  connector_did: "",
  connector_dsp_url: "",
  identity_hub_identity_url: "",
  identity_hub_api_key: "",
};

export function RequestVcPage() {
  const [form, setForm] = useState<VcForm>(emptyForm);
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const api = useApi();
  const { refreshUser, user } = useAuth();

  const update = <K extends keyof VcForm>(key: K, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  // Pre-fill from existing participant data
  const prefill = () => {
    if (user?.participant?.data_space_components) {
      const dsc = user.participant.data_space_components;
      setForm({
        connector_did: dsc.connector_did || "",
        connector_dsp_url: dsc.connector_dsp_url || "",
        identity_hub_identity_url: dsc.identity_hub_identity_url || "",
        identity_hub_api_key: dsc.identity_hub_api_key || "",
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setMessage("");

    try {
      const result = await api.requestVc(form);
      setStatus("success");
      setMessage(result.message || "VCs issued successfully!");
      await refreshUser();
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "VC request failed");
    }
  };

  return (
    <div className="page">
      <h1>Request Verifiable Credentials</h1>
      <p className="subtitle">
        Provide your connector and Identity Hub details to request VC issuance and register in the federated catalog.
      </p>

      {user?.participant?.data_space_components &&
        Object.keys(user.participant.data_space_components).length > 0 && (
          <button type="button" className="btn btn-secondary" onClick={prefill} style={{ marginBottom: 16 }}>
            Pre-fill from existing configuration
          </button>
        )}

      <form onSubmit={handleSubmit} className="form">
        <fieldset>
          <legend>Connector Details</legend>
          <div className="form-grid">
            <div className="form-field">
              <label>Connector DID *</label>
              <input
                required
                value={form.connector_did}
                onChange={(e) => update("connector_did", e.target.value)}
                placeholder="did:web:your-ih:participant-name"
              />
            </div>
            <div className="form-field">
              <label>Connector DSP URL *</label>
              <input
                required
                value={form.connector_dsp_url}
                onChange={(e) => update("connector_dsp_url", e.target.value)}
                placeholder="https://your-connector/api/dsp"
              />
            </div>
            <div className="form-field">
              <label>Identity Hub Identity URL *</label>
              <input
                required
                value={form.identity_hub_identity_url}
                onChange={(e) => update("identity_hub_identity_url", e.target.value)}
                placeholder="https://your-ih/api/identity"
              />
            </div>
            <div className="form-field">
              <label>Identity Hub API Key *</label>
              <input
                required
                value={form.identity_hub_api_key}
                onChange={(e) => update("identity_hub_api_key", e.target.value)}
                placeholder="super-user API key"
              />
            </div>
          </div>
        </fieldset>

        {status === "success" && <div className="success-banner">{message}</div>}
        {status === "error" && <div className="error-banner">{message}</div>}

        <button type="submit" className="btn btn-primary" disabled={status === "submitting"}>
          {status === "submitting" ? "Requesting…" : "Request VCs"}
        </button>
      </form>
    </div>
  );
}
