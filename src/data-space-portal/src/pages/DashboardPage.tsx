import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { useApi } from "../api/apiClient";

function Row({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null;
  return (
    <div className="detail-row">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value}</span>
    </div>
  );
}

export function DashboardPage() {
  const { user, logout } = useAuth();
  const api = useApi();
  const [showOffboardConfirm, setShowOffboardConfirm] = useState(false);
  const [offboardReason, setOffboardReason] = useState("");
  const [offboardError, setOffboardError] = useState("");
  const [offboarding, setOffboarding] = useState(false);

  const handleSelfOffboard = async () => {
    setOffboarding(true);
    setOffboardError("");
    try {
      await api.offboardSelf(offboardReason || undefined);
      logout();
    } catch (err: any) {
      setOffboardError(err.message || "Offboarding failed");
      setOffboarding(false);
    }
  };

  if (!user) {
    return <div className="page"><p>Loading…</p></div>;
  }

  const p = user.participant;
  const dsc = p?.data_space_components;
  const loc = p?.location;

  // Build address string from all available parts
  const addressLine = loc
    ? [loc.street, loc.building_number].filter(Boolean).join(" ")
    : null;
  const cityLine = loc
    ? [loc.postal_code, loc.city].filter(Boolean).join(" ")
    : null;

  return (
    <div className="page">
      <h1>{p?.full_name ?? user.name ?? user.preferred_username}</h1>

      {showOffboardConfirm && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>⚠️ Leave Data Space</h3>
            <p>
              This will permanently remove <strong>{p?.full_name ?? "your organization"}</strong> from
              the Data Space. Your portal access will be revoked immediately.
            </p>
            <div className="form-field">
              <label>Reason (optional)</label>
              <input
                value={offboardReason}
                onChange={(e) => setOffboardReason(e.target.value)}
                placeholder="e.g. No longer needed…"
              />
            </div>
            {offboardError && <div className="error-banner">{offboardError}</div>}
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={handleSelfOffboard} disabled={offboarding}>
                {offboarding ? "Removing…" : "Confirm — Leave Data Space"}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => { setShowOffboardConfirm(false); setOffboardReason(""); setOffboardError(""); }}
                disabled={offboarding}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h3>🏢 Organization</h3>
        <div className="detail-grid">
          <Row label="Full Name"   value={p?.full_name} />
          <Row label="Short Name"  value={p?.name} />
          <Row label="VAT Number"  value={p?.VAT_number} />
          <Row label="Email"       value={p?.email ?? user.email} />
          {loc && (
            <>
              <Row label="Country"       value={loc.country} />
              <Row label="City"          value={cityLine} />
              <Row label="Street"        value={addressLine} />
            </>
          )}
        </div>
      </div>

      {dsc && Object.keys(dsc).length > 0 && (
        <>
          {dsc.connector_dsp_url && (
            <div className="card">
              <h3>🔌 Connector</h3>
              <div className="detail-grid">
                <div className="detail-row">
                  <span className="detail-label">DSP URL</span>
                  <span className="detail-value">
                    <a href={dsc.connector_dsp_url} target="_blank" rel="noopener noreferrer">{dsc.connector_dsp_url}</a>
                  </span>
                </div>
              </div>
            </div>
          )}

          {(dsc.connector_did || dsc.identity_hub_identity_url) && (
            <div className="card">
              <h3>🪪 Identity Hub</h3>
              <div className="detail-grid">
                {dsc.connector_did && (
                  <div className="detail-row">
                    <span className="detail-label">DID</span>
                    <span className="detail-value">
                      <code style={{ fontSize: "0.85em", wordBreak: "break-all" }}>{dsc.connector_did}</code>
                    </span>
                  </div>
                )}
                {dsc.identity_hub_identity_url && (
                  <div className="detail-row">
                    <span className="detail-label">Identity URL</span>
                    <span className="detail-value">
                      <a href={dsc.identity_hub_identity_url} target="_blank" rel="noopener noreferrer">{dsc.identity_hub_identity_url}</a>
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      <div className="card">
        <h3>⚠️ Leave Data Space</h3>
        <p className="text-muted" style={{ fontSize: "13px", marginBottom: "12px" }}>
          Permanently removes your organization and revokes all access.
        </p>
        <button className="btn btn-danger btn-sm" onClick={() => setShowOffboardConfirm(true)}>
          Leave Data Space
        </button>
      </div>
    </div>
  );
}
