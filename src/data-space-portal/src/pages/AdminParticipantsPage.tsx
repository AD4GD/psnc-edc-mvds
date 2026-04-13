import { useState, useEffect, useCallback } from "react";
import { useApi, type Participant } from "../api/apiClient";
import { DataTable } from "../components/DataTable";

function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.${d.getFullYear()}`;
}

export function AdminParticipantsPage() {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [offboarding, setOffboarding] = useState<string | null>(null);
  const [offboardReason, setOffboardReason] = useState("");
  const [offboardError, setOffboardError] = useState("");
  const api = useApi();

  const fetchParticipants = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.listParticipants();
      setParticipants([...data].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
      setError("");
    } catch (err: any) {
      if (err.message?.includes("204") || err.message?.includes("No participant")) {
        setParticipants([]);
        setError("");
      } else {
        setError(err.message || "Failed to load participants");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchParticipants();
  }, [fetchParticipants]);

  const handleOffboard = async (id: string) => {
    setOffboardError("");
    try {
      await api.offboardParticipant(id, offboardReason || undefined);
      setOffboarding(null);
      setOffboardReason("");
      await fetchParticipants();
    } catch (err: any) {
      setOffboardError(err.message || "Offboarding failed");
    }
  };

  const columns = [
    {
      header: "Name",
      render: (p: Participant) => (
        <>
          <strong>{p.full_name}</strong>
          <div className="text-muted">{p.name}</div>
        </>
      ),
    },
    { header: "VAT", render: (p: Participant) => p.VAT_number },
    { header: "Email", render: (p: Participant) => p.email },
    {
      header: "Location",
      render: (p: Participant) =>
        p.location ? `${p.location.city}, ${p.location.country}` : "—",
    },
    {
      header: "Joined",
      render: (p: Participant) => p.created_at ? formatDate(p.created_at) : "—",
    },
    {
      header: "Actions",
      stopPropagation: true,
      render: (p: Participant) => (
        <button
          className="btn btn-danger btn-sm"
          onClick={() => { setOffboarding(p.id); setOffboardError(""); setOffboardReason(""); }}
        >
          Offboard
        </button>
      ),
    },
  ];

  return (
    <>
      {offboarding && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>⚠️ Offboard Participant</h3>
            <p>
              This will remove{" "}
              <strong>{participants.find((p) => p.id === offboarding)?.full_name}</strong>{" "}
              from the Data Space, revoke their portal access, and notify them by email.
            </p>
            <div className="form-field">
              <label>Reason (optional)</label>
              <input
                value={offboardReason}
                onChange={(e) => setOffboardReason(e.target.value)}
                placeholder="e.g. Contract expired, policy violation…"
              />
            </div>
            {offboardError && <div className="error-banner">{offboardError}</div>}
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={() => handleOffboard(offboarding)}>
                Confirm Offboarding
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => { setOffboarding(null); setOffboardReason(""); setOffboardError(""); }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <DataTable
        title="Participants"
        columns={columns}
        rows={participants}
        keyFn={(p) => p.id}
        loading={loading}
        error={error}
        emptyMessage="No participants found."
        onRefresh={fetchParticipants}
      />
    </>
  );
}
