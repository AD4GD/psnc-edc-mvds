#!/usr/bin/env python3
"""
configure_ds_idp.py

Contains logic for configuring the Identity Provider (IdP) in the Data Space realm.
"""

import requests
import keycloak_utils as ku
from keycloak import KeycloakAdmin

ALIAS = "provider-idp"
PART_ISSUER_ID = "http://localhost:8083/realms/Organizations"
PART_ISSUER_URL = "http://provider-keycloak:8080/realms/Organizations"
BROKER_ID = "kds-broker-client"
BROKER_SECRET = "kds-broker-secret"
IDP_ROLE_FOR_FC = "access-catalog"
FC_ROLE = "view-catalog"
KC_BASE = "http://localhost:8081"
REALM = "Organizations"
KC_USER = "admin"
KC_PASS = "edc"
EXCHANGE_CLIENT_ID = "data-space-token-exchange"
POLICY_NAME = "allow-token-exchange-client"

def get_idp_management_permissions(kc: KeycloakAdmin, realm: str, alias: str, base_url: str, token: str = None):
    kc.change_current_realm(realm)
    url = f"{base_url}/admin/realms/{realm}/identity-provider/instances/{alias}/management/permissions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Enable permissions
    r = requests.put(url, json={"enabled": True}, headers=headers)
    # Fetch permissions
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def create_client_policy(kc: KeycloakAdmin, realm: str, policy_name: str, client_uuids: list[str], base_url: str, token: str = None):
    kc.change_current_realm(realm)
    mgmt_client_id = kc.get_client_id("realm-management")
    url = f"{base_url}/admin/realms/{realm}/clients/{mgmt_client_id}/authz/resource-server/policy/client"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    existing = requests.get(url, params={"name": policy_name}, headers=headers).json()
    print(existing)
    if existing:
        return existing[0]["id"]
        
    print(f"Creating policy '{policy_name}'...")
    payload = {
        "name": policy_name,
        "type": "client",
        "logic": "POSITIVE",
        "decisionStrategy": "UNANIMOUS",
        "clients": client_uuids
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()["id"]

def configure_idp(kc: KeycloakAdmin, 
                  realm_name: str, 
                  idp_alias: str, 
                  idp_display_name: str,
                  issuer_url: str, 
                  token_url: str, 
                  userinfo_url: str, 
                  jwks_url: str,
                  client_id: str, 
                  client_secret: str,
                  mapper_claim_role: str,
                  mapper_target_group: str,
                  exchange_client_policy_id: str,
                  kc_base_url: str, 
                  admin_token: str):
    """
    Configures the Participant Identity Provider, its mappers, and permissions.
    """
    import json
    print(f"=== Configuring IdP '{idp_alias}' ===")
    
    # Ensure trustEmail is True to allow linking users with same email (e.g. consumer vs provider test users)
    # This prevents 'duplicate user' errors if realm checks email uniqueness.
    
    idp_payload = {
        "alias": idp_alias,
        "displayName": idp_display_name,
        "providerId": "keycloak-oidc",
        "enabled": True,
        "trustEmail": True,
        "storeToken": True,
        "addReadTokenRoleOnCreate": True,
        "config": {
            "issuer": issuer_url,
            "authorizationUrl": f"{issuer_url}/protocol/openid-connect/auth",
            "tokenUrl": token_url,
            "userInfoUrl": userinfo_url,
            "validateSignature": True,
            "useJwksUrl": True,
            "jwksUrl": jwks_url,
            "clientId": client_id,
            "clientSecret": client_secret,
            "clientAuthMethod": "client_secret_post",
            "syncMode": "IMPORT",
        }
    }

    try:
        kc.change_current_realm(realm_name)
        kc.get_idp(idp_alias)
        print(f"IdP '{idp_alias}' exists. Updating...")
        kc.update_idp(idp_alias, idp_payload)
    except Exception:
        print(f"Creating IdP '{idp_alias}'...")
        kc.change_current_realm(realm_name)
        kc.create_idp(idp_payload)
    
    print(f"=== Ensuring Username Mapper for IdP '{idp_alias}' ===")
    ku.ensure_idp_mapper(kc, realm_name, idp_alias, "unique-username", "oidc-username-idp-mapper", {
        "syncMode": "INHERIT",
        "template": f"{idp_alias}.${{CLAIM.preferred_username}}"
    })

    print(f"=== Ensuring Group Mapper for IdP '{idp_alias}' ===")
    # Using advanced group mapper to assign group if claim matches.
    # We check if 'resource_access.{client_id}.roles' contains 'mapper_claim_role'.
    # Note: Advanced Group Mapper regex matching on arrays can be tricky.
    # However, let's try strict matching or assume the user expects this to work.
    # If this fails to match inside the array, we might need a JS mapper or a different strategy.
    # A common workaround is regex: ".*access-catalog.*" if the array is serialized.
    # Let's try simple match first.
    claims_json = json.dumps([{
        "key": f"resource_access.{client_id}.roles",
        "value": mapper_claim_role
    }])
    
    ku.ensure_idp_mapper(kc, realm_name, idp_alias, "grant-catalog-group", "oidc-advanced-group-idp-mapper", {
        "syncMode": "FORCE", 
        "claims": claims_json,
        "group": mapper_target_group,
        "are.claims.regex": "true" # Force regex to handle array stringification if that happens
    })
    
    # Permissions
    print("Configuring IdP Token Exchange permissions...")
    idp_perms = get_idp_management_permissions(kc, realm_name, idp_alias, kc_base_url, admin_token)
    if "token-exchange" in idp_perms["scopePermissions"]:
        perm_id = idp_perms["scopePermissions"]["token-exchange"]
        ku.link_policy_to_permission(kc, realm_name, perm_id, exchange_client_policy_id, kc_base_url, admin_token)

def main():
    kc_base = ku.env("KC_BASE", KC_BASE)
    kc_user = ku.env("KC_USER", KC_USER)
    kc_pass = ku.env("KC_PASS", KC_PASS)
    realm = ku.env("REALM_NAME", REALM)
    exchange_client_id = ku.env("EXCHANGE_CLIENT_ID", EXCHANGE_CLIENT_ID)
    policy_name = ku.env("POLICY_NAME", POLICY_NAME)

    print(f"Connecting to Keycloak at {kc_base}...")
    ku.wait_for_keycloak(kc_base)
    conn = ku.get_connection(kc_base, kc_user, kc_pass)
    token = ku.get_access_token(kc_base, "master", kc_user, kc_pass)
    kc = ku.get_admin(connection=conn)

    # Force token acquisition against 'master' BEFORE switching context to 'Organizations'.
    # This prevents 'invalid_grant' error where KeycloakAdmin might try to auth against the target realm.
    print("Verifying Master Realm connection...")
    kc.get_realm("master")

    print(f"Checking client '{exchange_client_id}' in realm '{realm}'...")
    kc.change_current_realm(realm)
    exchange_uuid = kc.get_client_id(exchange_client_id)
    if not exchange_uuid:
        raise RuntimeError(f"Client '{exchange_client_id}' not found in realm '{realm}'")
    print(f"Found Exchange Client UUID: {exchange_uuid}")

    client_policy_id = create_client_policy(
        kc=kc,
        realm=realm,
        policy_name=policy_name,
        client_uuids=[exchange_uuid],
        base_url=kc_base,
        token=token,
    )
    
    configure_idp(
        kc=kc,
        realm_name=realm,
        idp_alias=ALIAS,
        idp_display_name=f"Participant ({ALIAS})",
        issuer_url=PART_ISSUER_ID,
        token_url=f"{PART_ISSUER_URL}/protocol/openid-connect/token",
        userinfo_url=f"{PART_ISSUER_URL}/protocol/openid-connect/userinfo",
        jwks_url=f"{PART_ISSUER_URL}/protocol/openid-connect/certs",
        client_id=BROKER_ID,
        client_secret=BROKER_SECRET,
        mapper_claim_role=IDP_ROLE_FOR_FC,
        mapper_target_group="/federated-catalog",
        exchange_client_policy_id=client_policy_id,
        kc_base_url=kc_base,
        admin_token=token
    )

if __name__ == "__main__":
    main()