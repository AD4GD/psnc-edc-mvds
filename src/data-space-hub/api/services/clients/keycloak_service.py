import base64
import json
from typing import Any, Dict

from api.core.logging_config import setup_logging
from api.core.settings import KeycloakSettings
from keycloak import KeycloakOpenID

logger = setup_logging()


class KeycloakService:
    """Synchronous service for interacting with Keycloak."""

    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=KeycloakSettings.keycloak_server_url,
            realm_name=KeycloakSettings.keycloak_realm,
            client_id=KeycloakSettings.keycloak_client_id,
            verify=True,
        )
        # optional client secret for client-credentials grant
        self.client_secret = getattr(KeycloakSettings, "keycloak_client_secret", None)

    def health(self) -> bool:
        """Check Keycloak server health."""
        try:
            conf = self.keycloak_openid.well_known()
            return "issuer" in conf
        except Exception as e:
            logger.error(f"Keycloak health check failed: {e}")
            return False

    # --- token acquisition helpers ---

    def login_user(self, username: str, password: str, scope: str = "openid") -> Dict[str, Any]:
        """
        Obtain token using Resource Owner Password Credentials (username/password).
        Returns token dict containing access_token / refresh_token / expires_in etc.
        """
        try:
            return self.keycloak_openid.token(username, password, scope=scope)
        except Exception as e:
            logger.error(f"Keycloak login_user failed for {username}: {e}")
            raise

    def login_client(self) -> Dict[str, Any]:
        """
        Obtain token using client credentials grant. Requires KeycloakSettings.keycloak_client_secret.
        Returns token dict.
        """
        if not self.client_secret:
            raise RuntimeError("Client secret not configured for Keycloak client-credentials")
        try:
            return self.keycloak_openid.token_grant(client_secret=self.client_secret)
        except Exception:
            # fallback: call token with empty username/password but grant_type=client_credentials
            try:
                return self.keycloak_openid.token(grant_type="client_credentials", client_secret=self.client_secret)
            except Exception as e:
                logger.error(f"Keycloak client login failed: {e}")
                raise

    # --- introspection / userinfo ---

    def introspect_token(self, token: str) -> dict:
        """Introspect access token (active/inactive and token metadata)."""
        try:
            data = self.keycloak_openid.introspect(token)
            if not data.get("active"):
                raise ValueError("Inactive token")
            return data
        except Exception as e:
            logger.error(f"Keycloak introspection failed: {e}")
            raise

    def userinfo(self, token: str) -> dict:
        """Fetch user info."""
        try:
            return self.keycloak_openid.userinfo(token)
        except Exception as e:
            logger.error(f"Keycloak userinfo failed: {e}")
            raise

    # --- JWT payload helpers (lightweight, no crypto verification) ---

    @staticmethod
    def _decode_jwt_payload(token: str) -> Dict[str, Any]:
        """Decode JWT payload without verification to inspect claims."""
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return {}
            payload_b64 = parts[1]
            # add padding
            padding = "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            return json.loads(payload_bytes)
        except Exception as e:
            logger.debug(f"Failed to decode JWT payload: {e}")
            return {}

    def token_has_realm_role(self, token: str, role: str) -> bool:
        """Check whether token contains given realm role."""
        payload = self._decode_jwt_payload(token)
        roles = payload.get("realm_access", {}).get("roles", [])
        return role in roles

    def token_has_client_role(self, token: str, client: str, role: str) -> bool:
        """Check whether token contains given role for a client (resource_access)."""
        payload = self._decode_jwt_payload(token)
        client_roles = payload.get("resource_access", {}).get(client, {}).get("roles", [])
        return role in client_roles

    # --- authorization helpers for RS operations ---

    def require_admin(self, token: str) -> None:
        """
        Ensure the provided token corresponds to an admin authorized to manage participants.
        Raises ValueError on unauthorized.
        Checks:
          - realm role 'admin' or 'rs-admin'
          - or client role 'admin' for the configured client id
        """
        # prefer introspection to validate token
        try:
            self.introspect_token(token)
        except Exception:
            raise ValueError("Token invalid or inactive")

        # realm-level check
        if self.token_has_realm_role(token, "admin") or self.token_has_realm_role(token, "rs-admin"):
            return

        # client-level check (admin role on our client)
        client_id = KeycloakSettings.keycloak_client_id
        if client_id and self.token_has_client_role(token, client_id, "admin"):
            return

        raise ValueError("Insufficient permissions: admin role required")

    def authorized_for_participant(self, token: str, participant_did: str) -> bool:
        """
        Optional finer-grained check: whether token grants permission to manage given participant.
        Default returns True for admins, otherwise can be extended to check scopes/claims.
        """
        try:
            if self.token_has_realm_role(token, "admin") or self.token_has_realm_role(token, "rs-admin"):
                return True
            # example: check a claim 'managed_participants' in token payload
            payload = self._decode_jwt_payload(token)
            managed = payload.get("managed_participants", [])
            if participant_did in managed:
                return True
        except Exception:
            pass
        return False


keycloak_service = KeycloakService()
