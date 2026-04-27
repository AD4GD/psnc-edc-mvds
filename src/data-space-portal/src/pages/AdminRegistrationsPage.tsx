import { useState, useEffect, useCallback } from "react";
import { useApi, type RegistrationRequest } from "../api/apiClient";
import { DataTable } from "../components/DataTable";

function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.${d.getFullYear()}`;
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
      setRegistrations([...data].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
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

  const columns = [
    {
      header: "Company",
      render: (r: RegistrationRequest) => {
        const form = r.request_form;
        return (
          <>
            <strong>{form?.full_name || form?.name || "—"}</strong>
            {form?.VAT_number && <div className="text-muted">{form.VAT_number}</div>}
          </>
        );
      },
    },
    {
      header: "Email",
      render: (r: RegistrationRequest) => r.request_form?.email || "—",
    },
    {
      header: "Status",
      render: (r: RegistrationRequest) => statusBadge(r.status),
    },
    {
      header: "Email Confirmed",
      render: (r: RegistrationRequest) => (r.email_confirmed ? "✅" : "❌"),
    },
    {
      header: "Submitted",
      render: (r: RegistrationRequest) => r.created_at ? formatDate(r.created_at) : "—",
    },
    {
      header: "Actions",
      stopPropagation: true,
      render: (r: RegistrationRequest) => {
        const canAction = r.status === "REQUESTED" && r.email_confirmed;
        const canRetry = canAction && !!r.error_detail;
        const actionMsg = actionStatus[r.id];
        return (
          <>
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
                {r.status !== "REQUESTED" ? "Already processed" : "Awaiting email confirmation"}
              </span>
            )}
            {r.error_detail && !canRetry && (
              <div className="text-error">{r.error_detail}</div>
            )}
          </>
        );
      },
    },
  ];

  return (
    <DataTable
      title="Registration Requests"
      columns={columns}
      rows={registrations}
      keyFn={(r) => r.id}
      loading={loading}
      error={error}
      emptyMessage="No registration requests found."
      onRefresh={fetchRegistrations}
    />
  );
}