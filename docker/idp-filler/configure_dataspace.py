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

# --- Registration Service Logic ---

def wait_for_registration_service(rs_url: str, timeout: int = 2):
    print("=== Waiting for registration service ===")
    ready = False
    for _ in range(60):
        try:
            # We use a simple health check or just try to connect
            requests.get(rs_url, timeout=timeout)
            ready = True
            break
        except:
            time.sleep(1)
    
    if not ready:
        print("[WARN] Registration service not ready, skipping auto-registration")
        return -1

    print("=== Registration service is ready ===")
    return 0

def register_participant(rs_url: str, token : str, did : str, participant_url: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Register Participant
        print(f"Registering participant DID '{did}'...")
        requests.post(f"{rs_url}/authority/registry/participants", 
                      params={"did": did, "protocolUrl": participant_url}, 
                      headers=headers)
        
    except Exception as e:
        print(f"Failed to register participants: {e}")

# --- Main ---

def main():
    KC_BASE = ku.env("KC_BASE", "http://localhost:8081")
    KC_USER = ku.env("KC_USER", "admin")
    KC_PASS = ku.env("KC_PASS", "edc")
    REALM = ku.env("REALM_NAME", "Organizations") # Data Space Realm
    DAPS_REALM = "DAPS"
    
    RS_URL = ku.env("WEB_HTTP_RS_URI", "http://localhost:38182")
    RS_USER = ku.env("RS_USERNAME", "rs-admin")
    RS_PASS = ku.env("RS_PASSWORD", "edc")

    ku.wait_for_keycloak(KC_BASE)
    conn = ku.get_connection(KC_BASE, KC_USER, KC_PASS)
    token = ku.get_access_token(KC_BASE, "master", KC_USER, KC_PASS)
    kc = ku.get_admin(connection=conn)

    print("=== Configuring Master Realm ===")
    ku.ensure_realm(kc, "master")
    
    # --- DAPS Configuration ---
    print("=== Configuring DAPS Realm ===")
    ku.ensure_realm(kc, DAPS_REALM, base_file="daps_realm.json")
    
    # DAPS Clients
    daps_clients = {
        "consumer": "client_consumer_daps.json",
        "provider": "client_provider_daps.json",
        "sage": "client_sage_daps.json",
        "federated-catalog": "client_fc_daps.json",
    }
    
    for alias, fname in daps_clients.items():
        if os.path.exists(fname):
            with open(fname, "r") as f:
                cdef = json.load(f)
                ku.ensure_client(kc, DAPS_REALM, cdef)
                cert_path = f"certs/{alias}-daps.jks"
                if os.path.exists(cert_path):
                    ku.upload_certificate(kc, DAPS_REALM, cdef.get("clientId"), cert_path, KC_BASE, alias="dapsPrivate", password="1234", token=token)

    time.sleep(5) # Wait for the clients to be created
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

    register_participant(RS_URL, ku.get_access_token(KC_BASE, REALM, RS_USER, RS_PASS), "consumer", "https://consumer-connector-edc-connector.apps.bst2.paas.psnc.pl/protocol")
    register_participant(RS_URL, ku.get_access_token(KC_BASE, REALM, RS_USER, RS_PASS), "provider", "https://provider-connector-edc-connector.apps.bst2.paas.psnc.pl/protocol")
    register_participant(RS_URL, ku.get_access_token(KC_BASE, REALM, RS_USER, RS_PASS), "sage", "https://sage-connector-edc-connector.apps.bst2.paas.psnc.pl/protocol")
         
    print("=== Data Space Configuration Complete ===")

if __name__ == "__main__":
    main()
