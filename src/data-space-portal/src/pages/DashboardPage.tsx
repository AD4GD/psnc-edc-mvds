import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { useApi } from "../api/apiClient";

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
      logout(); // session is gone, KC user deleted
    } catch (err: any) {
      setOffboardError(err.message || "Offboarding failed");
      setOffboarding(false);
    }
  };

  if (!user) {
    return (
      <div className="page">
        <p>Loading user information…</p>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Dashboard</h1>

      {/* Self-offboard confirmation modal */}
      {showOffboardConfirm && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>⚠️ Leave Data Space</h3>
            <p>
              This will permanently remove <strong>{user.participant?.full_name ?? "your organization"}</strong> from
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
        <h3>👤 Your Profile</h3>
        <div className="detail-grid">
          <div className="detail-row">
            <span className="detail-label">Name</span>
            <span className="detail-value">{user.name || user.preferred_username}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Email</span>
            <span className="detail-value">{user.email}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Role</span>
            <span className="detail-value">
              {user.is_admin ? (
                <span className="badge badge-admin">Admin</span>
              ) : (
                <span className="badge badge-participant">Participant</span>
              )}
            </span>
          </div>
        </div>
      </div>

      {user.participant && (
        <div className="card">
          <h3>🏢 Your Organization</h3>
          <div className="detail-grid">
            <div className="detail-row">
              <span className="detail-label">Name</span>
              <span className="detail-value">{user.participant.full_name}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">VAT</span>
              <span className="detail-value">{user.participant.VAT_number}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Email</span>
              <span className="detail-value">{user.participant.email}</span>
            </div>
            {user.participant.data_space_components &&
              Object.keys(user.participant.data_space_components).length > 0 && (
                <div className="detail-row">
                  <span className="detail-label">Connector DID</span>
                  <span className="detail-value">
                    {user.participant.data_space_components.connector_did || "Not configured"}
                  </span>
                </div>
              )}
          </div>

          <div style={{ marginTop: "20px", borderTop: "1px solid #f0f0f0", paddingTop: "16px" }}>
            <button
              className="btn btn-danger btn-sm"
              onClick={() => setShowOffboardConfirm(true)}
            >
              Leave Data Space
            </button>
            <p className="text-muted" style={{ fontSize: "12px", marginTop: "6px" }}>
              Permanently removes your organization and revokes your access.
            </p>
          </div>
        </div>
      )}

      {!user.participant && !user.is_admin && (
        <div className="card">
          <h3>⏳ No Participant Linked</h3>
          <p>
            Your account is not yet linked to a participant organization. If you've recently been
            approved, please refresh the page or contact the Data Space admin.
          </p>
        </div>
      )}
    </div>
  );
}
