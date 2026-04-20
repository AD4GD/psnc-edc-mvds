import { useState, useEffect, useCallback } from "react";
import { useApi, type IssuedVc } from "../api/apiClient";
import { useAuth } from "../auth/AuthContext";
import { DataTable } from "../components/DataTable";

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

function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.${d.getFullYear()}`;
}

export function RequestVcPage() {
  const [form, setForm] = useState<VcForm>(emptyForm);
  const [submitStatus, setSubmitStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [issuedVcs, setIssuedVcs] = useState<IssuedVc[]>([]);
  const [vcsLoading, setVcsLoading] = useState(true);
  const [vcsError, setVcsError] = useState("");
  const [copied, setCopied] = useState<string | null>(null);
  const api = useApi();
  const { refreshUser, user } = useAuth();

  const fetchVcs = useCallback(async () => {
    try {
      setVcsLoading(true);
      const data = await api.getMyVcs();
      setIssuedVcs([...data].sort((a, b) =>
        new Date(b.issued_at ?? 0).getTime() - new Date(a.issued_at ?? 0).getTime()
      ));
      setVcsError("");
    } catch (err: any) {
      setVcsError(err.message || "Failed to load issued VCs");
    } finally {
      setVcsLoading(false);
    }
  }, []);

  useEffect(() => { fetchVcs(); }, [fetchVcs]);

  const update = <K extends keyof VcForm>(key: K, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const prefill = () => {
    if (user?.participant?.data_space_components) {
      const dsc = user.participant.data_space_components as Record<string, string>;
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
    setSubmitStatus("submitting");
    setMessage("");
    try {
      const result = await api.requestVc(form);
      setSubmitStatus("success");
      setMessage(result.message || "VCs issued successfully!");
      await refreshUser();
      await fetchVcs();
    } catch (err: any) {
      setSubmitStatus("error");
      setMessage(err.message || "VC request failed");
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(id);
      setTimeout(() => setCopied(null), 2000);
    });
  };

  const buildCurl = (vc: IssuedVc): string => {
    const ihUrl = vc.credential_metadata?.connector_dsp_url
      ? vc.credential_storage_ref
      : vc.credential_storage_ref ?? "<IDENTITY_HUB_URL>";
    const did = vc.credential_metadata?.connector_did ?? "<CONNECTOR_DID>";
    const b64did = btoa(did);
    const rawVc = vc.credential_metadata?.raw_vc ?? "{}";
    return `curl -X POST "${ihUrl}/v1alpha/participants/${b64did}/credentials" \\
  -H "x-api-key: <API_KEY>" \\
  -H "Content-Type: application/json" \\
  -d '${rawVc}'`;
  };

  const vcColumns = [
    {
      header: "Issued",
      render: (vc: IssuedVc) => vc.issued_at ? formatDate(vc.issued_at) : "—",
    },
    {
      header: "Type",
      render: (vc: IssuedVc) => vc.credential_type ?? "—",
    },
    {
      header: "Connector DID",
      render: (vc: IssuedVc) => (
        <code style={{ fontSize: "0.8em", wordBreak: "break-all" }}>
          {vc.credential_metadata?.connector_did ?? "—"}
        </code>
      ),
    },
    {
      header: "Status",
      render: (vc: IssuedVc) => (
        <span className={`badge ${vc.status === "active" ? "badge-onboarded" : "badge-rejected"}`}>
          {vc.status}
        </span>
      ),
    },
    {
      header: "Actions",
      stopPropagation: true,
      render: (vc: IssuedVc) => (
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
          {vc.credential_metadata?.raw_vc && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => copyToClipboard(vc.credential_metadata!.raw_vc!, `vc-${vc.id}`)}
            >
              {copied === `vc-${vc.id}` ? "✓ Copied" : "Copy VC"}
            </button>
          )}
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => copyToClipboard(buildCurl(vc), `curl-${vc.id}`)}
          >
            {copied === `curl-${vc.id}` ? "✓ Copied" : "Copy curl"}
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="page">
      <h1>Verifiable Credentials</h1>
      <p className="subtitle">
        Provide your connector and Identity Hub details to request VC issuance and register in the federated catalog.
      </p>

      <form onSubmit={handleSubmit} className="form">
        <fieldset>
          <legend>Connector</legend>
          <div className="form-grid">
            <div className="form-field">
              <label>DSP URL *</label>
              <input
                required
                value={form.connector_dsp_url}
                onChange={(e) => update("connector_dsp_url", e.target.value)}
                placeholder="https://your-connector/api/dsp"
              />
            </div>
          </div>
        </fieldset>

        <fieldset>
          <legend>Identity Hub</legend>
          <div className="form-grid">
            <div className="form-field">
              <label>DID *</label>
              <input
                required
                value={form.connector_did}
                onChange={(e) => update("connector_did", e.target.value)}
                placeholder="did:web:your-ih:participant-name"
              />
            </div>
            <div className="form-field">
              <label>Identity URL *</label>
              <input
                required
                value={form.identity_hub_identity_url}
                onChange={(e) => update("identity_hub_identity_url", e.target.value)}
                placeholder="https://your-ih/api/identity"
              />
            </div>
            <div className="form-field">
              <label>API Key *</label>
              <input
                required
                value={form.identity_hub_api_key}
                onChange={(e) => update("identity_hub_api_key", e.target.value)}
                placeholder="super-user API key"
              />
            </div>
          </div>
        </fieldset>

        {submitStatus === "success" && <div className="success-banner">{message}</div>}
        {submitStatus === "error" && <div className="error-banner">{message}</div>}

        <button type="submit" className="btn btn-primary" disabled={submitStatus === "submitting"}>
          {submitStatus === "submitting" ? "Requesting…" : "Request VCs"}
        </button>
      </form>

      <div style={{ marginTop: "2.5rem" }}>
        <DataTable
          title="Issued VCs"
          columns={vcColumns}
          rows={issuedVcs}
          keyFn={(vc) => vc.id}
          loading={vcsLoading}
          error={vcsError}
          emptyMessage="No VCs have been issued yet."
          onRefresh={fetchVcs}
        />
      </div>
    </div>
  );
}


