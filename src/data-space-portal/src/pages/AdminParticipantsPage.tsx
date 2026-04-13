import { useState, useEffect, useCallback } from "react";
import { useApi } from "../api/apiClient";

interface Participant {
  id: string;
  name: string;
  full_name: string;
  VAT_number: string;
  email: string;
  location: {
    country: string;
    city: string;
    postal_code: string;
    street: string;
    building_number: string;
  } | null;
  data_space_components: Record<string, any>;
  created_at: string;
}

interface FcTarget {
  participantId: string;
  url: string;
  name?: string;
  supportedProtocols?: string[];
}

export function AdminParticipantsPage() {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [fcTargets, setFcTargets] = useState<FcTarget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [offboarding, setOffboarding] = useState<string | null>(null); // id being offboarded
  const [offboardReason, setOffboardReason] = useState("");
  const [offboardError, setOffboardError] = useState("");
  const api = useApi();

  const fetchParticipants = useCallback(async () => {
    try {
      setLoading(true);
      const [data, targets] = await Promise.all([
        api.listParticipants(),
        api.getFcTargets().catch(() => [] as FcTarget[]),
      ]);
      setParticipants(data);
      setFcTargets(targets);
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

  /** Find the FC target node for a participant by matching their connector DID. */
  function getFcStatusForParticipant(p: Participant): FcTarget | null {
    const did = p.data_space_components?.connector_did;
    if (!did) return null;
    return fcTargets.find((t) => t.participantId === did) ?? null;
  }

  if (loading) return <div className="page"><p>Loading participants…</p></div>;

  return (
    <div className="page">
      <h1>Participants</h1>

      {error && <div className="error-banner">{error}</div>}

      {/* Offboard confirmation modal */}
      {offboarding && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>⚠️ Offboard Participant</h3>
            <p>
              This will remove <strong>{participants.find((p) => p.id === offboarding)?.full_name}</strong> from
              the Data Space, revoke their portal access, and notify them by email.
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
              <button
                className="btn btn-danger"
                onClick={() => handleOffboard(offboarding)}
              >
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

      {participants.length === 0 ? (
        <p>No participants found.</p>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>VAT</th>
                <th>Email</th>
                <th>Location</th>
                <th>FC Status</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {participants.map((p) => {
                const fcTarget = getFcStatusForParticipant(p);
                return (
                  <tr key={p.id} onClick={() => setExpanded(expanded === p.id ? null : p.id)} className="clickable-row">
                    <td>
                      <strong>{p.full_name}</strong>
                      <div className="text-muted">{p.name}</div>
                    </td>
                    <td>{p.VAT_number}</td>
                    <td>{p.email}</td>
                    <td>
                      {p.location
                        ? `${p.location.city}, ${p.location.country}`
                        : "—"}
                    </td>
                    <td>
                      {fcTarget ? (
                        <div className="fc-status fc-status--active">
                          <span className="fc-status__dot fc-status__dot--green" title="Registered in Federated Catalog" />
                          <span className="fc-status__label">In catalog</span>
                          <div className="fc-status__url text-muted">{fcTarget.url}</div>
                        </div>
                      ) : (
                        <div className="fc-status fc-status--inactive">
                          <span className="fc-status__dot fc-status__dot--red" title="Not registered in Federated Catalog" />
                          <span className="fc-status__label">Not in catalog</span>
                        </div>
                      )}
                    </td>
                    <td>{p.created_at ? new Date(p.created_at).toLocaleDateString() : "—"}</td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => { setOffboarding(p.id); setOffboardError(""); setOffboardReason(""); }}
                      >
                        Offboard
                      </button>
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
