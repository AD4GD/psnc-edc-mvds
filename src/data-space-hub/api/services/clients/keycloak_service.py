import base64
import json
import secrets
import string
from typing import Any, Dict, Optional

from api.core.logging_config import setup_logging
from api.core.settings import KeycloakSettings
from keycloak import KeycloakAdmin, KeycloakOpenID

logger = setup_logging()


class KeycloakService:
    """Synchronous service for interacting with Keycloak."""

    def __init__(self):
        self.client_secret = KeycloakSettings.keycloak_client_secret
        self.keycloak_openid = KeycloakOpenID(
            server_url=KeycloakSettings.keycloak_server_url,
            realm_name=KeycloakSettings.keycloak_realm,
            client_id=KeycloakSettings.keycloak_client_id,
            client_secret_key=self.client_secret,
            verify=True,
        )

        # Admin client for user management (lazy init)
        self._keycloak_admin: Optional[KeycloakAdmin] = None

    def _create_keycloak_admin(self) -> KeycloakAdmin:
        """Create a fresh KeycloakAdmin instance."""
        return KeycloakAdmin(
            server_url=KeycloakSettings.keycloak_server_url,
            username=KeycloakSettings.keycloak_admin_username,
            password=KeycloakSettings.keycloak_admin_password,
            realm_name=KeycloakSettings.keycloak_realm,
            user_realm_name="master",
            client_id="admin-cli",
            verify=True,
        )

    @property
    def keycloak_admin(self) -> KeycloakAdmin:
        """Lazy-initialised KeycloakAdmin instance with automatic token refresh."""
        if self._keycloak_admin is None:
            self._keycloak_admin = self._create_keycloak_admin()
        else:
            # Re-authenticate if the admin token has expired to avoid 401 errors
            try:
                self._keycloak_admin.get_server_info()
            except Exception:
                logger.info("Keycloak admin token expired or invalid, re-authenticating")
                self._keycloak_admin = self._create_keycloak_admin()
        return self._keycloak_admin

    def health(self) -> bool:
        """Check Keycloak server health."""
        conf = self.keycloak_openid.well_known()
        return "issuer" in conf

    # --- token acquisition helpers ---

    def login_user(self, username: str, password: str, scope: str = "openid") -> Dict[str, Any]:
        """
        Obtain token using Resource Owner Password Credentials (username/password).
        Returns token dict containing access_token / refresh_token / expires_in etc.
        """
        return self.keycloak_openid.token(username, password, scope=scope)

    def login_client(self) -> Dict[str, Any]:
        """
        Obtain token using client credentials grant. Requires KeycloakSettings.keycloak_client_secret.
        Returns token dict.
        """
        if not self.client_secret:
            raise RuntimeError("Client secret not configured for Keycloak client-credentials")
        try:
            return self.keycloak_openid.token_grant(client_secret=self.client_secret)
        except Exception:  # pylint: disable=W0718
            # fallback: call token with empty username/password but grant_type=client_credentials
            try:
                return self.keycloak_openid.token(grant_type="client_credentials", client_secret=self.client_secret)
            except Exception:
                logger.error("Keycloak client login failed")
                raise RuntimeError("Keycloak client login failed")

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
    def decode_jwt_payload(token: str) -> Dict[str, Any]:
        """Decode JWT payload without verification to inspect claims."""
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        # add padding
        padding = "=" * (-len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        return json.loads(payload_bytes)

    def token_has_realm_role(self, token: str, role: str) -> bool:
        """Check whether token contains given realm role."""
        payload = self.decode_jwt_payload(token)
        roles = payload.get("realm_access", {}).get("roles", [])
        return role in roles

    def token_has_client_role(self, token: str, client: str, role: str) -> bool:
        """Check whether token contains given role for a client (resource_access)."""
        payload = self.decode_jwt_payload(token)
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
        if self.token_has_realm_role(token, "admin") or self.token_has_realm_role(token, "rs-admin"):
            return True
        # example: check a claim 'managed_participants' in token payload
        payload = self.decode_jwt_payload(token)
        managed = payload.get("managed_participants", [])
        if participant_did in managed:
            return True
        return False

    # --- user management (KeycloakAdmin) ---

    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        *,
        enabled: bool = True,
        email_verified: bool = True,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new user in Keycloak. Returns the Keycloak user id.

        For company/organisation accounts firstName = short name, lastName = legal name.
        requiredActions is set to UPDATE_PASSWORD only so Keycloak will not ask the
        user to fill in profile fields that are already populated.
        """
        payload: Dict[str, Any] = {
            "email": email,
            "username": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": enabled,
            "emailVerified": email_verified,
            # Only ask for a password change on first login – profile is already complete.
            "requiredActions": ["UPDATE_PASSWORD"],
        }
        if attributes:
            payload["attributes"] = attributes

        try:
            user_id = self.keycloak_admin.create_user(payload, exist_ok=False)
            logger.info(f"Created Keycloak user {email} -> {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Failed to create Keycloak user {email}: {e}")
            raise

    def send_required_action_email(self, user_id: str, actions: Optional[list] = None) -> None:
        """
        Trigger Keycloak required-action emails (e.g. UPDATE_PASSWORD).
        NOTE: Requires Keycloak SMTP to be configured. Prefer set_temporary_password() instead.
        """
        if actions is None:
            actions = ["UPDATE_PASSWORD"]
        try:
            self.keycloak_admin.send_update_account(user_id=user_id, payload=actions)
            logger.info(f"Sent required-action email to user {user_id}: {actions}")
        except Exception as e:
            logger.error(f"Failed to send required-action email to {user_id}: {e}")
            raise

    def set_temporary_password(self, user_id: str, length: int = 16) -> str:
        """
        Generate a random temporary password and set it on the Keycloak user
        with 'temporary=True' so the user is prompted to change it on first login.

        Also ensures UPDATE_PROFILE is NOT in requiredActions so the user is
        never shown the "Update Account Information" form (profile is pre-filled
        from registration data).

        Returns the generated password.
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        temp_password = "".join(secrets.choice(alphabet) for _ in range(length))
        try:
            self.keycloak_admin.set_user_password(
                user_id=user_id,
                password=temp_password,
                temporary=True,
            )
            logger.info(f"Set temporary password for user {user_id}")

            # setting temporary=True may cause Keycloak to append UPDATE_PASSWORD to
            # requiredActions; make sure UPDATE_PROFILE is absent so the user is not
            # asked to fill in profile fields that are already populated.
            user = self.keycloak_admin.get_user(user_id)
            required_actions = user.get("requiredActions", [])
            cleaned = [a for a in required_actions if a != "UPDATE_PROFILE"]
            if cleaned != required_actions:
                self.keycloak_admin.update_user(
                    user_id=user_id,
                    payload={"requiredActions": cleaned},
                )
                logger.info(f"Removed UPDATE_PROFILE from requiredActions for user {user_id}")

            return temp_password
        except Exception as e:
            logger.error(f"Failed to set temporary password for user {user_id}: {e}")
            raise

    def assign_realm_role(self, user_id: str, role_name: str) -> None:
        """Assign a realm-level role to a user."""
        try:
            role = self.keycloak_admin.get_realm_role(role_name)
            self.keycloak_admin.assign_realm_roles(user_id=user_id, roles=[role])
            logger.info(f"Assigned role '{role_name}' to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to assign role '{role_name}' to user {user_id}: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Look up a user by email. Returns user dict or None."""
        users = self.keycloak_admin.get_users(query={"email": email, "exact": True})
        return users[0] if users else None

    def delete_user_by_email(self, email: str) -> bool:
        """
        Delete the Keycloak user with the given email.
        Returns True if deleted, False if the user was not found.
        Raises on unexpected errors.
        """
        user = self.get_user_by_email(email)
        if not user:
            logger.warning(f"Keycloak user not found for email {email} – skipping KC deletion")
            return False
        user_id = user["id"]
        self.keycloak_admin.delete_user(user_id)
        logger.info(f"Deleted Keycloak user {email} ({user_id})")
        return True

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract the Keycloak 'sub' (user id) from a bearer token."""
        payload = self.decode_jwt_payload(token)
        return payload.get("sub")

    def get_participant_id_from_token(self, token: str) -> Optional[str]:
        """Extract the 'participant_id' attribute from the token claims or user attributes."""
        payload = self.decode_jwt_payload(token)
        # First check if it's directly in the token (if mapped via protocol mapper)
        pid = payload.get("participant_id")
        if pid:
            return pid
        # Fallback: look up user attributes via userinfo
        try:
            info = self.userinfo(token)
            return info.get("participant_id")
        except Exception:
            return None


keycloak_service = KeycloakService()
