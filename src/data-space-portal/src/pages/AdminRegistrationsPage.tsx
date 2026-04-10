import { useState, useEffect, useCallback } from "react";
import { useApi } from "../api/apiClient";

interface RegistrationRequest {
  id: string;
  status: string;
  email_confirmed: boolean;
  error_detail: string;
  request_form: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export function AdminRegistrationsPage() {
  const [registrations, setRegistrations] = useState<RegistrationRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionStatus, setActionStatus] = useState<Record<string, string>>({});
  const [rejectReasons, setRejectReasons] = useState<Record<string, string>>({});
  const api = useApi();

  const fetchRegistrations = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.listRegistrations();
      setRegistrations(data);
      setError("");
    } catch (err: any) {
      if (err.message?.includes("204") || err.message?.includes("No registration")) {
        setRegistrations([]);
        setError("");
      } else {
        setError(err.message || "Failed to load registrations");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRegistrations();
  }, [fetchRegistrations]);

  const handleApprove = async (id: string) => {
    setActionStatus((prev) => ({ ...prev, [id]: "approving" }));
    try {
      await api.approveRegistration(id);
      setActionStatus((prev) => ({ ...prev, [id]: "approved" }));
      await fetchRegistrations();
    } catch (err: any) {
      setActionStatus((prev) => ({ ...prev, [id]: `error: ${err.message}` }));
    }
  };

  const handleReject = async (id: string) => {
    const reason = rejectReasons[id] || "";
    setActionStatus((prev) => ({ ...prev, [id]: "rejecting" }));
    try {
      await api.rejectRegistration(id, reason);
      setActionStatus((prev) => ({ ...prev, [id]: "rejected" }));
      await fetchRegistrations();
    } catch (err: any) {
      setActionStatus((prev) => ({ ...prev, [id]: `error: ${err.message}` }));
    }
  };

  const handleRetry = async (id: string) => {
    setActionStatus((prev) => ({ ...prev, [id]: "retrying" }));
    try {
      await api.retryOnboarding(id);
      setActionStatus((prev) => ({ ...prev, [id]: "retried" }));
      await fetchRegistrations();
    } catch (err: any) {
      setActionStatus((prev) => ({ ...prev, [id]: `error: ${err.message}` }));
    }
  };

  const statusBadge = (s: string) => {
    const map: Record<string, string> = {
      REQUESTED: "badge-requested",
      APPROVED: "badge-approved",
      REJECTED: "badge-rejected",
      ONBOARDED: "badge-onboarded",
    };
    return <span className={`badge ${map[s] || ""}`}>{s}</span>;
  };

  if (loading) return <div className="page"><p>Loading registrations…</p></div>;

  return (
    <div className="page">
      <h1>Registration Requests</h1>

      {error && <div className="error-banner">{error}</div>}

      {registrations.length === 0 ? (
        <p>No registration requests found.</p>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Email</th>
                <th>Status</th>
                <th>Email Confirmed</th>
                <th>Submitted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {registrations.map((r) => {
                const form = r.request_form;
                const canAction = r.status === "REQUESTED" && r.email_confirmed;
                const hasError = !!r.error_detail;
                const canRetry = r.status === "REQUESTED" && r.email_confirmed && hasError;
                const actionMsg = actionStatus[r.id];
                return (
                  <tr key={r.id}>
                    <td>
                      <strong>{form?.full_name || form?.name || "—"}</strong>
                      {form?.VAT_number && <div className="text-muted">{form.VAT_number}</div>}
                    </td>
                    <td>{form?.email || "—"}</td>
                    <td>{statusBadge(r.status)}</td>
                    <td>{r.email_confirmed ? "✅" : "❌"}</td>
                    <td>{r.created_at ? new Date(r.created_at).toLocaleDateString() : "—"}</td>
                    <td>
                      {canRetry && (
                        <div className="error-banner" style={{ marginBottom: "0.5rem", fontSize: "0.85rem" }}>
                          ⚠️ Previous onboarding failed: {r.error_detail}
                        </div>
                      )}
                      {canAction ? (
                        <div className="action-group">
                          {canRetry ? (
                            <button
                              className="btn btn-sm btn-approve"
                              onClick={() => handleRetry(r.id)}
                              disabled={!!actionMsg}
                            >
                              🔄 Retry Onboarding
                            </button>
                          ) : (
                            <button
                              className="btn btn-sm btn-approve"
                              onClick={() => handleApprove(r.id)}
                              disabled={!!actionMsg}
                            >
                              Approve
                            </button>
                          )}
                          <div className="reject-group">
                            <input
                              type="text"
                              placeholder="Reason (optional)"
                              value={rejectReasons[r.id] || ""}
                              onChange={(e) =>
                                setRejectReasons((prev) => ({ ...prev, [r.id]: e.target.value }))
                              }
                              className="input-sm"
                            />
                            <button
                              className="btn btn-sm btn-reject"
                              onClick={() => handleReject(r.id)}
                              disabled={!!actionMsg}
                            >
                              Reject
                            </button>
                          </div>
                          {actionMsg && <span className="text-muted">{actionMsg}</span>}
                        </div>
                      ) : (
                        <span className="text-muted">
                          {r.status !== "REQUESTED"
                            ? "Already processed"
                            : "Awaiting email confirmation"}
                        </span>
                      )}
                      {r.error_detail && !canRetry && (
                        <div className="text-error">{r.error_detail}</div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
