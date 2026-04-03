#!/usr/bin/env python3
"""
participant_add_connector.py

Registers a new Connector in the Participant Keycloak.
This involves:
1. Creating a Client for the Connector (The Audience).
2. Creating a Role (Permission) for accessing this connector.
3. Creating a Group and assigning the Role to it.
4. Updating the 'data-space-users' client to allow it to issue tokens with this Audience (Scope/Mapper).
"""

import keycloak_utils as ku
from keycloak import KeycloakAdmin

# Input Args (Env)
CONNECTOR_CLIENT_ID = "provider-connector"
CONNECTOR_SECRET = "connector-secret"
CONNECTOR_ROLE = "access-connector"
# Defaults
PARTICIPANT_REALM_DEFAULT = "Organizations"
USER_CLIENT_ID = "data-space-users"
TEST_USER = f"psnc"
TEST_PASS = "edc"

KC_BASE = "http://localhost:48083"
KC_USER = "admin"
KC_PASS = "edc"
REALM = "Organizations"


def add_connector(kc: KeycloakAdmin, realm: str, connector_client_id: str, connector_secret: str, audience_role: str = "access-connector"):
    """
    Registers the connector in Keycloak.
    """
    print(f"=== Adding Connector '{connector_client_id}' to realm '{realm}' ===")
    
    # 1. Ensure Connector Client
    connector_uuid = ku.ensure_client(kc, realm, {
        "clientId": connector_client_id,
        "name": connector_client_id,
        "description": f"Connector Client for {connector_client_id}",
        "secret": connector_secret,
        "serviceAccountsEnabled": False,
        "standardFlowEnabled": False,
        "directAccessGrantsEnabled": False,
        "publicClient": False,
        "bearerOnly": False,
        "fullScopeAllowed": False
    })
    
    # 2. Ensure Role
    ku.ensure_client_role(kc, realm, connector_uuid, audience_role)
    
    # 3. Ensure Group
    group_name = f"group-{connector_client_id}"
    ku.ensure_group(kc, realm, group_name, clientRoles={
        connector_client_id: [audience_role]
    })

    # 4. User: test
    print(f"Ensuring test user '{TEST_USER}' with access to connector...")
    ku.ensure_user(kc, realm, TEST_USER, TEST_PASS, groups=[group_name])
    
    # 5. Update 'data-space-users' scope
    users_client_uuid = kc.get_client_id(USER_CLIENT_ID)
    if not users_client_uuid:
        print(f"[WARN] User client '{USER_CLIENT_ID}' not found. Skipping scope update.")
        return

    # 5.1 Assign Role to Scope
    print(f"Adding role '{audience_role}' to scope of '{USER_CLIENT_ID}'...")
    role_rep = kc.get_client_role(connector_uuid, audience_role)
    kc.assign_client_roles_to_client_scope(users_client_uuid, connector_uuid, [role_rep])

    # 5.2 Audience Mapper
    resolve_mapper = {
        "name": "audience-resolve",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-resolve-mapper",
        "consentRequired": False,
        "config": {} 
    }

    try:
        client_info = kc.get_client(client_id=users_client_uuid)
        current_mappers = client_info.get("protocolMappers", []) or []
        if not any(m['name'] == "audience-resolve" for m in current_mappers):
            kc.add_mapper_to_client(client_id=users_client_uuid, payload=resolve_mapper)
            print(f"Audience Resolve mapper added to '{USER_CLIENT_ID}'.")
        else:
            print(f"Audience Resolve mapper already exists on '{USER_CLIENT_ID}'.")
    except Exception as e:
        print(f"[WARN] Failed to add resolve mapper: {e}")
        
    print(f"=== Connector '{connector_client_id}' registered successfully. ===")


def main():
    ku.wait_for_keycloak(KC_BASE)
    conn = ku.get_connection(KC_BASE, KC_USER, KC_PASS)
    kc = ku.get_admin(connection=conn)
    kc.get_realm("master")

    add_connector(kc, REALM, CONNECTOR_CLIENT_ID, CONNECTOR_SECRET, CONNECTOR_ROLE)

if __name__ == "__main__":
    main()
