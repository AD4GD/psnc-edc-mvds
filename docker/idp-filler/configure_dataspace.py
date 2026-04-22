#!/usr/bin/env python3
"""
configure_dataspace.py

Configures the Data Space Keycloak.
Roles:
1. Act as the Trust Anchor / Central Identity Broker (DAPS + DataSpace).
2. Federated Catalog resides here.
3. Connectors exchange "External Node" tokens for "Internal Data Space" tokens.
"""

import os
import json
import time
import requests
import keycloak_utils as ku

KC_BASE = ku.env("KC_BASE", "http://localhost:8081")
KC_USER = ku.env("KC_USER", "admin")
KC_PASS = ku.env("KC_PASS", "edc")
REALM = ku.env("REALM_NAME", "Organizations") # Data Space Realm
DAPS_REALM = "DAPS"

RS_URL = ku.env("WEB_HTTP_RS_URI", "http://localhost:38182")
RS_USER = ku.env("RS_USERNAME", "rs-admin")
RS_PASS = ku.env("RS_PASSWORD", "edc")

# --- Registration Service Logic ---

# --- Main ---

def main():
    ku.wait_for_keycloak(KC_BASE)
    conn = ku.get_connection(KC_BASE, KC_USER, KC_PASS)
    kc = ku.get_admin(connection=conn)

    print("=== Configuring Master Realm ===")
    ku.ensure_realm(kc, "master")

    # --- Data Space Realm Configuration ---
    print("=== Configuring Data Space Realm ===")
    ku.ensure_realm(kc, REALM, base_file="organizations_realm.json")
    
    # 2. Clients
    # C. Data Space UI Client
    ku.ensure_client(kc, REALM, {
        "clientId": "data-space-users",
        "publicClient": True,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "redirectUris": ["*"],
        "webOrigins": ["*"]
    })
    # 3. Users (RS Admin)
    if RS_USER and RS_PASS:
        ku.ensure_user(kc, REALM, RS_USER, RS_PASS, email=f"{RS_USER}@example.com")

    print("=== Data Space Configuration Complete ===")

if __name__ == "__main__":
    main()
