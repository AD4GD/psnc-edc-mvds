import { useConfig } from "../config/ConfigContext";
import { useAuth } from "../auth/AuthContext";

/**
 * Returns a set of API helper functions that automatically include
 * the Keycloak bearer token on authenticated requests.
 */
export function useApi() {
  const { apiBaseUrl } = useConfig();
  const { token } = useAuth();

  function authHeaders(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (token) {
      h["Authorization"] = `Bearer ${token}`;
    }
    return h;
  }

  // ── Registration (public) ──────────────────────────────────────────

  async function submitRegistration(data: {
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
    };
  }) {
    const res = await fetch(`${apiBaseUrl}/v1/registration/request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // ── Auth ───────────────────────────────────────────────────────────

  async function getMe() {
    const res = await fetch(`${apiBaseUrl}/v1/auth/me`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // ── Registration admin ────────────────────────────────────────────

  async function listRegistrations(offset = 0, limit = 100) {
    const res = await fetch(
      `${apiBaseUrl}/v1/registration/request/list?offset=${offset}&limit=${limit}`,
      { headers: authHeaders() }
    );
    if (res.status === 204 || res.status === 404) return [];
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function getRegistration(id: string) {
    const res = await fetch(`${apiBaseUrl}/v1/registration/request/${id}`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function approveRegistration(id: string) {
    const res = await fetch(`${apiBaseUrl}/v1/registration/request/${id}/approve`, {
      method: "PUT",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function rejectRegistration(id: string, reason: string) {
    const res = await fetch(`${apiBaseUrl}/v1/registration/request/${id}/reject`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ reason }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function retryOnboarding(id: string) {
    const res = await fetch(`${apiBaseUrl}/v1/registration/request/${id}/retry`, {
      method: "PUT",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // ── Offboarding ───────────────────────────────────────────────────

  async function offboardParticipant(id: string, reason?: string) {
    const url = new URL(`${apiBaseUrl}/v1/participants/${id}`);
    if (reason) url.searchParams.set("reason", reason);
    const res = await fetch(url.toString(), {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function offboardSelf(reason?: string) {
    const url = new URL(`${apiBaseUrl}/v1/participants/me`);
    if (reason) url.searchParams.set("reason", reason);
    const res = await fetch(url.toString(), {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // ── Participants admin ────────────────────────────────────────────

  async function listParticipants(offset = 0, limit = 100) {
    const res = await fetch(
      `${apiBaseUrl}/v1/participants/list?offset=${offset}&limit=${limit}`,
      { headers: authHeaders() }
    );
    if (res.status === 204 || res.status === 404) return [];
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function getParticipant(id: string) {
    const res = await fetch(`${apiBaseUrl}/v1/participants/${id}`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  // ── VC request (authenticated participant) ────────────────────────

  async function requestVc(data: {
    connector_did: string;
    connector_dsp_url: string;
    identity_hub_identity_url: string;
    identity_hub_api_key: string;
  }) {
    const res = await fetch(`${apiBaseUrl}/v1/verifiable-credentials/request`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  return {
    submitRegistration,
    getMe,
    listRegistrations,
    getRegistration,
    approveRegistration,
    rejectRegistration,
    retryOnboarding,
    offboardParticipant,
    offboardSelf,
    listParticipants,
    getParticipant,
    requestVc,
  };
}
