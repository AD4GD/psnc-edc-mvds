#!/usr/bin/env python3
"""
configure_egi.py

Configures EGI Check-in as an Identity Provider in a single Keycloak instance.
This script can be run multiple times (once per Keycloak realm you want to configure).
"""

import requests
import keycloak_utils as ku
from keycloak import KeycloakAdmin

# TODO right now there is no support for PKCE
# TODO now llogout is on front-channel, but we should consider back-channel for better security and reliability (requires additional configuration on EGI side)

# Configuration - customize these for your deployment
KC_BASE = "http://localhost:8083"
REALM = "Organizations"
KC_USER = "admin"
KC_PASS = "edc"

EGI_DISCOVERY_ENDPOINT = "https://aai-dev.egi.eu/auth/realms/egi/.well-known/openid-configuration"
EGI_IDP_ALIAS = "EGI-Check-in"
EGI_IDP_DISPLAY_NAME = "EGI Check-in"
EGI_CLIENT_ID = "<client_id>"  # Replace with actual value
EGI_CLIENT_SECRET = "<client_secret>"  # Replace with actual value
EGI_SCOPES = "openid voperson_id email profile aarc offline_access"


def configure_egi_idp(
    kc: KeycloakAdmin, 
    realm_name: str, 
    discovery_endpoint: str,
    idp_alias: str,
    idp_display_name: str,
    client_id: str,
    client_secret: str,
    scopes: str
):
    """
    Configures EGI Check-in as an OIDC Identity Provider in the specified realm.
    
    Args:
        kc: KeycloakAdmin instance
        realm_name: Name of the realm to configure (e.g., "Organizations")
        discovery_endpoint: EGI Check-in discovery endpoint URL
        idp_alias: Alias for the IdP (e.g., "egi-check-in-oidc")
        idp_display_name: Display name shown to users
        client_id: OIDC Client ID from EGI Federation Registry
        client_secret: OIDC Client Secret from EGI Federation Registry
        scopes: Space-separated list of scopes
    """
    
    print(f"\n{'='*60}")
    print(f"Configuring EGI Check-in in realm '{realm_name}'")
    print(f"{'='*60}\n")
    
    kc.change_current_realm(realm_name)
    
    # Resolve endpoints from discovery document
    print("Resolving endpoints from discovery document...")
    try:
        discovery_resp = requests.get(discovery_endpoint, timeout=10)
        discovery_resp.raise_for_status()
        discovery_data : dict = discovery_resp.json()
        
        authorization_url = discovery_data.get("authorization_endpoint")
        token_url = discovery_data.get("token_endpoint")
        logout_url = discovery_data.get("end_session_endpoint")
        userinfo_url = discovery_data.get("userinfo_endpoint")
        jwks_url = discovery_data.get("jwks_uri")
        issuer = discovery_data.get("issuer")
        token_introspection_url = discovery_data.get("introspection_endpoint")
        
    except Exception as e:
        raise ValueError(f"Failed to resolve endpoints from discovery document: {e}")

    if not jwks_url:
        raise ValueError(
            "JWKS URL not found in discovery document. "
            "Either fix the discovery endpoint or disable JWKS validation."
        )
    
    if not authorization_url or not token_url:
        raise ValueError(
            "Authorization URL and Token URL are required but not found in discovery document."
        )

    # IdP Configuration
    idp_payload = {
        "alias": idp_alias,
        "displayName": idp_display_name,
        "providerId": "oidc",
        "enabled": True,
        "trustEmail": False,
        "storeToken": False,
        "config": {
            "authorizationUrl": authorization_url,
            "tokenUrl": token_url,
            "userInfoUrl": userinfo_url,
            "tokenIntrospectionUrl": token_introspection_url,
            "issuer": issuer,
            "jwksUrl": jwks_url,
            "logoutUrl": logout_url,
            "clientId": client_id,
            "clientSecret": client_secret,
            "defaultScope": scopes,
            "useJwksUrl": "true",
            "validateSignature": "true",
            "clientAuthMethod": "client_secret_post",
            "tokenIntrospectionEndpointAuthMethod": "client_secret_post",
            "syncMode": "IMPORT",
            "userNameAttributeName": "sub",
            "linkOnly": "false",
            "pkceMethod": "true",
            # "pkceMethod": "false",
            "frontchannelLogout": "false",
            "backchannel_logout_session_required": "false",
            "validateLogoutSignature": "false"
        }
    }
    
    # Create or update IdP
    try:
        existing_idp = kc.get_idp(idp_alias)
        print(f"✓ IdP '{idp_alias}' exists. Removing and recreating...")
        kc.delete_idp(idp_alias)
        kc.create_idp(idp_payload)
        print(f"✓ IdP '{idp_alias}' created...")
    except Exception as e:
        print(f"✓ Creating IdP '{idp_alias}'...")
        kc.create_idp(idp_payload)
    
    print(f"✓ IdP '{idp_alias}' configured successfully")
    
    # Configure Mappers
    print(f"\n{'='*60}")
    print(f"Configuring Attribute Mappers")
    print(f"{'='*60}\n")
    
    # Mapper 1: Subject (unique identifier from EGI - used as NameID)
    print("Creating subject mapper...")
    ku.ensure_idp_mapper(
        kc, 
        realm_name, 
        idp_alias, 
        "subject",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "IMPORT",
            "claim": "sub",
            "user.attribute": "oidc_sub"
        }
    )
    print("✓ subject mapper created")
    
    # Mapper 2: Username (from preferred_username)
    print("Creating username mapper...")
    ku.ensure_idp_mapper(
        kc, 
        realm_name, 
        idp_alias, 
        "username",
        "oidc-username-idp-mapper",
        {
            "syncMode": "IMPORT",
            "template": "${CLAIM.preferred_username}"
        }
    )
    print("✓ username mapper created")
    
    # Mapper 2: Email
    print("Creating email mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "email",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "email",
            "user.attribute": "email"
        }
    )
    print("✓ email mapper created")
    
    # Mapper 3: First Name
    print("Creating firstName mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "firstName",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "given_name",
            "user.attribute": "firstName"
        }
    )
    print("✓ firstName mapper created")
    
    # Mapper 4: Last Name
    print("Creating lastName mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "lastName",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "family_name",
            "user.attribute": "lastName"
        }
    )
    print("✓ lastName mapper created")
    
    # Mapper 5: Entitlements (group memberships from EGI VOs) via AARC scope
    print("Creating entitlements mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "entitlements",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "eduperson_entitlement",
            "user.attribute": "entitlements"
        }
    )
    print("✓ entitlements mapper created")
    
    # Mapper 5b: AARC (newer comprehensive scope replacing deprecated attributes)
    print("Creating aarc mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "aarc",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "aarc",
            "user.attribute": "aarc"
        }
    )
    print("✓ aarc mapper created")
    
    # Mapper 6: Home Organization
    print("Creating homeOrganization mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "homeOrganization",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "schac_home_organization",
            "user.attribute": "homeOrganization"
        }
    )
    print("✓ homeOrganization mapper created")
    
    # Mapper 7: External Affiliation
    print("Creating externalAffiliation mapper...")
    ku.ensure_idp_mapper(
        kc,
        realm_name,
        idp_alias,
        "externalAffiliation",
        "oidc-user-attribute-idp-mapper",
        {
            "syncMode": "INHERIT",
            "claim": "voperson_external_affiliation",
            "user.attribute": "externalAffiliation"
        }
    )
    print("✓ externalAffiliation mapper created")
    
    print(f"\n{'='*60}")
    print(f"✓ EGI Check-in configuration complete!")
    print(f"{'='*60}\n")



def main():
    """
    Main entry point.
    Configures EGI Check-in for the specified Keycloak realm.
    """
    
    # Get configuration from environment or use defaults
    kc_base = ku.env("KC_BASE", KC_BASE)
    kc_user = ku.env("KC_USER", KC_USER)
    kc_pass = ku.env("KC_PASS", KC_PASS)
    realm = ku.env("REALM_NAME", REALM)
    
    egi_discovery = ku.env("EGI_DISCOVERY_ENDPOINT", EGI_DISCOVERY_ENDPOINT)
    egi_client_id = ku.env("EGI_CLIENT_ID", EGI_CLIENT_ID)
    egi_client_secret = ku.env("EGI_CLIENT_SECRET", EGI_CLIENT_SECRET)
    egi_alias = ku.env("EGI_IDP_ALIAS", EGI_IDP_ALIAS)
    egi_display_name = ku.env("EGI_IDP_DISPLAY_NAME", EGI_IDP_DISPLAY_NAME)
    egi_scopes = ku.env("EGI_SCOPES", EGI_SCOPES)
    
    # Validation
    if egi_client_id == "YOUR_CLIENT_ID_FROM_EGI_REGISTRY":
        print("\n❌ ERROR: EGI_CLIENT_ID not configured!")
        print("Please set the EGI_CLIENT_ID environment variable with the value from EGI Federation Registry\n")
        exit(1)
    
    if egi_client_secret == "YOUR_CLIENT_SECRET_FROM_EGI_REGISTRY":
        print("\n❌ ERROR: EGI_CLIENT_SECRET not configured!")
        print("Please set the EGI_CLIENT_SECRET environment variable with the value from EGI Federation Registry\n")
        exit(1)
    
    print(f"\nConfiguring Keycloak at {kc_base}")
    print(f"Target Realm: {realm}")
    print(f"EGI IdP Alias: {egi_alias}\n")
    
    # Wait for Keycloak to be ready
    ku.wait_for_keycloak(kc_base)
    
    # Connect to Keycloak
    conn = ku.get_connection(kc_base, kc_user, kc_pass)
    kc = ku.get_admin(connection=conn)
    
    # Verify master realm connection
    print("Verifying Master Realm connection...")
    try:
        kc.get_realm("master")
        print("✓ Master realm connection verified\n")
    except Exception as e:
        print(f"❌ Failed to connect to master realm: {e}")
        exit(1)
    
    # Configure EGI Check-in
    try:
        configure_egi_idp(
            kc=kc,
            realm_name=realm,
            discovery_endpoint=egi_discovery,
            idp_alias=egi_alias,
            idp_display_name=egi_display_name,
            client_id=egi_client_id,
            client_secret=egi_client_secret,
            scopes=egi_scopes
        )
    except Exception as e:
        print(f"\n❌ Error configuring EGI Check-in: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("✓ All done!")


if __name__ == "__main__":
    main()