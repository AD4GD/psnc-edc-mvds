#!/usr/bin/env python3
"""
configure_participant.py

Configures the Participant Keycloak (e.g., Consumer/Provider).
Roles:
1. Provide identity to Users via 'data-space-users' client.
2. Act as OIDC Provider for Data Space via 'kds-broker-client'.
"""

import sys

try:
    from . import keycloak_utils as ku
except ImportError:
    import keycloak_utils as ku

def main():
    KC_BASE = ku.env("KEYCLOAK_ADDRESS", "http://keycloak.domain.com")
    KC_USER = ku.env("KEYCLOAK_ADMIN_USER", "admin")
    KC_PASS = ku.env("KEYCLOAK_ADMIN_PASSWORD", "edc")
    REALM = ku.env("REALM_NAME", "Organizations")
    
    TEST_USER = ku.env("USER_NAME", "test")
    TEST_PASS = ku.env("USER_PASS", "edc")

    FC_ROLE = "access-catalog"
    FC_GROUP = ku.env("FC_GROUP", "federated-catalog")
    
    # Secrets
    CATALOG_SECRET = ku.env("CATALOG_CLIENT_SECRET", "catalog-secret")

    ku.wait_for_keycloak(KC_BASE)
    conn = ku.get_connection(KC_BASE, KC_USER, KC_PASS)
    kc = ku.get_admin(connection=conn)

    print("=== Configuring Master Realm ===")
    ku.ensure_realm(kc, "master")

    # 1. Ensure Realm
    ku.ensure_realm(kc, REALM, base_file="organizations_realm.json")
    
    # 2. Client: data-space-users (Public, for user login)
    # B. federated-catalog (The target audience)
    catalog_uuid = ku.ensure_client(kc, REALM, {
        "clientId": "federated-catalog",
        "name": "federated-catalog",
        "description": "Private client for Federated Catalog access",
        "secret": CATALOG_SECRET,
        "serviceAccountsEnabled": False,
        "standardFlowEnabled": False,
        "publicClient": False,
        "fullScopeAllowed": False,
    })
    data_space_users_uuid = ku.ensure_client(kc, REALM, {
        "clientId": "data-space-users",
        "name": "data-space-users",
        "description": "Public client for browser-based login (SPA)",
        "rootUrl": "",
        "adminUrl": "",
        "baseUrl": "",
        "surrogateAuthRequired": False,
        "enabled": True,
        "alwaysDisplayInConsole": False,
        "clientAuthenticatorType": "client-secret",
        "redirectUris": [
            "*"
        ],
        "webOrigins": [
            "*",
            "/*"
        ],
        "notBefore": 0,
        "bearerOnly": False,
        "consentRequired": False,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": True,
        "serviceAccountsEnabled": False,
        "publicClient": True,
        "frontchannelLogout": True,
        "protocol": "openid-connect",
        "attributes": {
            "pkce.code.challenge.method": "S256",
            "backchannel.logout.session.required": "True"
        },
        "authenticationFlowBindingOverrides": {},
        "fullScopeAllowed": False,
        "nodeReRegistrationTimeout": -1,
        "defaultClientScopes": [
            "web-origins",
            "acr",
            "profile",
            "roles",
            "email",
            "basic"
        ],
        "optionalClientScopes": [
            "address",
            "phone",
            "offline_access",
            "microprofile-jwt"
        ]
    })

    # D. Clients configuration 
    # D.1 Federated Catalog Client
    ku.ensure_client_role(kc, REALM, catalog_uuid, FC_ROLE)

    kc.assign_client_roles_to_client_scope(data_space_users_uuid, catalog_uuid, [{"name" : FC_ROLE}])

    # Ensure group for federated catalog
    ku.ensure_group(kc, REALM, FC_GROUP, clientRoles={
        "federated-catalog": [FC_ROLE]
    })

    # Make this group the default for newly self-registered users
    ku.ensure_realm_default_groups(kc, REALM, [FC_GROUP])
    
    # 5. User: test
    ku.ensure_user(kc, REALM, TEST_USER, TEST_PASS, groups=[FC_GROUP])
    
    print("=== Participant Configuration Complete ===", file=sys.stderr)

if __name__ == "__main__":
    main()
