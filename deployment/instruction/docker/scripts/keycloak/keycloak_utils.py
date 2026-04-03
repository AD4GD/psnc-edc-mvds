import os
import sys
import time
import json
from typing import Dict, List
import requests
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

def env(key, default):
    return os.environ.get(key, default)

def wait_for_keycloak(url : str):
    print(f"Waiting for Keycloak at {url}...")
    for _ in range(60):
        print(f"Checking {url}...")
        try:
            # allow_redirects=False ensures we don't follow Keycloak's 302 redirect to localhost (KC_HOSTNAME)
            r = requests.get(url, timeout=2, allow_redirects=False)
            print(f"Status code: {r.status_code}")
            # Accept 200 OK or 302 Found (Redirection means server is up)
            if r.status_code in [200, 301, 302] or r.status_code < 500:
                print("Keycloak is ready.")
                return
        except Exception as e:
            print(f"Connection attempt failed: {e}")
        time.sleep(2)
    print("[ERROR] Keycloak did not start")
    exit(1)

def get_connection(base : str, user : str, password : str) -> KeycloakOpenIDConnection:
    return KeycloakOpenIDConnection(
        server_url=base + ("/" if not base.endswith("/") else ""),
        username=user,
        password=password,
        realm_name="master",
        verify=True
    )


def get_admin(base: str = None, user: str = None, password: str = None, connection: KeycloakOpenIDConnection = None) -> KeycloakAdmin:
    # keycloak library typically appends /auth if needed, but for quarkus (kc > 17) it's just base/
    # If base is http://host:port, we use that.
    if connection is not None:
        return KeycloakAdmin(connection=connection)
    return KeycloakAdmin(
        server_url=base + ("/" if not base.endswith("/") else ""),
        username=user,
        password=password,
        realm_name="master",
        verify=True
    )

def get_access_token(base_url : str, realm : str, username : str, password : str) -> str:
    r = requests.post(
        f"{base_url}/realms/{realm}/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": username,
            "password": password,
            "grant_type": "password"
        }
    ).json()
    return r.get("access_token")

def ensure_realm(kc: KeycloakAdmin, realm_name: str, require_https: bool = False, payload: dict = None, base_file: str = None):
    # Check if exists
    desired_ssl = "none" if not require_https else "all"
    try:
        kc.get_realm(realm_name)
        print(f"[WARN] Realm '{realm_name}' exists.")
        
        # Ensure SSL is none or as required
        current = kc.get_realm(realm_name)
        if current.get("sslRequired") != desired_ssl:
            print(f"Updating realm '{realm_name}' sslRequired to '{desired_ssl}'...")
            current["sslRequired"] = desired_ssl
            kc.update_realm(realm_name, current)
            
    except:
        print(f"Creating realm '{realm_name}'...")
        if payload is None:
            if base_file is not None and os.path.exists(base_file):
                with open(base_file, "r") as f:
                    payload = json.load(f)
            else:
                # Minimal fallback
                payload = {"realm": realm_name, "enabled": True}
        
        payload["realm"] = realm_name
        payload["sslRequired"] = desired_ssl
        kc.create_realm(payload)

def ensure_idp_mapper(kc: KeycloakAdmin, realm: str, idp_alias: str, name: str,
                        mapper_type: str, config: Dict[str, str]) -> None:
    """Ensure an IdP mapper exists."""
    kc.change_current_realm(realm)
    
    # Check if exists
    try:
        mappers = kc.get_idp_mappers(idp_alias)
    except Exception:
        mappers = []
        
    for m in mappers:
        if m['name'] == name:
            # Update? Simplified: just return if exists, or delete and recreate
            print(f"    Mapper '{name}' exists for IdP '{idp_alias}'", file=sys.stderr)
            return

    print(f"=== Creating mapper '{name}' for IdP '{idp_alias}' ===", file=sys.stderr)
    kc.add_mapper_to_idp(idp_alias, {
        "name": name,
        "identityProviderAlias": idp_alias,
        "identityProviderMapper": mapper_type,
        "config": config
    })

def ensure_client(kc: KeycloakAdmin, realm: str, client_def: dict) -> str:
    kc.change_current_realm(realm)
    cid = client_def.get("clientId")
    print(f"Creating client '{cid}' in realm '{realm}'...")
    found_id = kc.get_client_id(cid)
    if found_id is None:
        return kc.create_client(client_def)
    else:
        print(found_id)
        client_def["id"] = found_id
        return kc.create_client(client_def, skip_exists=True)
    
def link_policy_to_permission(kc : KeycloakAdmin, realm : str, permission_id: str, policy_id: str, base_url: str, token: str = None):
    kc.change_current_realm(realm)
    mgmt_client_id = kc.get_client_id("realm-management")
    url = f"{base_url}/admin/realms/{realm}/clients/{mgmt_client_id}/authz/resource-server/policy/{permission_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    policy_def = r.json()
    
    current_policies = policy_def.get("policies", [])
    if policy_id not in current_policies:
        print(f"Linking policy to permission {policy_def['name']}...")
        current_policies.append(policy_id)
        policy_def["policies"] = current_policies
        r = requests.put(url, json=policy_def, headers=headers)
        r.raise_for_status()

def ensure_client_role(kc: KeycloakAdmin, realm: str, client_uuid: str, role_name: str):
    kc.change_current_realm(realm)
    print(f"Creating client role '{role_name}' for client {client_uuid}...")
    kc.create_client_role(client_uuid, {"name": role_name}, skip_exists=True)

def ensure_group(kc: KeycloakAdmin, realm: str, group_name: str, clientRoles: Dict[str, List[str]] = {}) -> str:
    kc.change_current_realm(realm)
    print(f"Ensuring group '{group_name}' in realm '{realm}'...")
    
    group_id = None
    all_groups = kc.get_groups()
    existing = next((g for g in all_groups if g['name'] == group_name), None)
    
    if existing:
        group_id = existing['id']
    else:
        group_id = kc.create_group({"name": group_name})

    if clientRoles and group_id:
        for client_alias, role_names in clientRoles.items():
            client_uuid = kc.get_client_id(client_alias)
            if not client_uuid:
                print(f"[WARN] Client '{client_alias}' not found. Skipping group role assignment.")
                continue
            
            role_reps = []
            for rname in role_names:
                try:
                    r = kc.get_client_role(client_uuid, rname)
                    role_reps.append(r)
                except Exception:
                    print(f"[WARN] Role '{rname}' not found in client '{client_alias}'")
            
            if role_reps:
                kc.assign_group_client_roles(group_id, client_uuid, role_reps)
                print(f"Assigned roles {role_names} from client '{client_alias}' to group '{group_name}'")
    
    return group_id

def ensure_user(kc: KeycloakAdmin, realm: str, username: str, password: str, email : str = None, roles_map : Dict[str, List[str]] = None, groups : List[str] = None) -> str:
    kc.change_current_realm(realm)
    uid = kc.get_user_id(username)
    if not uid:
        print(f"Creating user '{username}' in realm '{realm}'...")
        kc.create_user({
            "username": username,
            "firstName": username,
            "lastName": username,
            "enabled": True, 
            "email": email or f"{username}@example.com", 
            "emailVerified": True
        })
        uid = kc.get_user_id(username)
    
    kc.set_user_password(uid, password, temporary=False)
    
    if roles_map:
        # roles_map = { "client_id": ["role1", "role2"] }
        for cid, roles in roles_map.items():
            client_uuid = kc.get_client_id(cid)
            if not client_uuid:
                continue
            
            # Resolve role objects
            role_objs = []
            for rname in roles:
                try:
                    ro = kc.get_client_role(client_uuid, rname)
                    role_objs.append(ro)
                except Exception as e:
                    print(f"[WARN] Role {rname} not found in {cid}: {e}")
            
            if role_objs:
                kc.assign_client_role(uid, client_uuid, role_objs)
    if groups:
        for gname in groups:
            _groups = kc.get_groups()
            group = next((g for g in _groups if g['name'] == gname), None)
            if not group:
                continue
            gid = group.get("id")
            if gid:
                kc.group_user_add(uid, gid)
    return uid


def ensure_realm_default_groups(kc: KeycloakAdmin, realm: str, group_paths: List[str]) -> None:
    """Ensure default groups for realm self-registration.

    Keycloak stores this in RealmRepresentation.defaultGroups (paths like "/group").
    This corresponds to UI: Realm settings -> User registration -> Default groups.
    """
    kc.change_current_realm(realm)

    current = kc.get_realm(realm)
    existing = set(current.get("defaultGroups") or [])
    desired = {p if p.startswith("/") else f"/{p}" for p in group_paths}

    if desired.issubset(existing):
        return

    current["defaultGroups"] = sorted(existing | desired)
    kc.update_realm(realm, current)

def upload_certificate(kc: KeycloakAdmin, realm: str, client_id: str, cert_path: str, base_url: str, alias="dapsPrivate", password="1234", token: str = None):
    """
    Uploads a JKS certificate for a client.
    Uses direct API call since python-keycloak might vary in support.
    """
    if not os.path.exists(cert_path):
        print(f"[ERROR] Certificate file not found: {cert_path}")
        return

    # Need internal ID
    kc.change_current_realm(realm)
    internal_id = kc.get_client_id(client_id)
    if not internal_id:
        print(f"Client {client_id} not found for certificate upload")
        return

    url = f"{base_url}/admin/realms/{realm}/clients/{internal_id}/certificates/jwt.credential/upload-certificate"
    
    # We need the raw token
    
    
    print(f"Uploading certificate for {client_id}...")
    with open(cert_path, "rb") as fh:
        files = {"file": (os.path.basename(cert_path), fh, "application/octet-stream")}
        data = {
            "keystoreFormat": "JKS",
            "keyAlias": alias,
            "storePassword": password,
        }
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, data=data)
            if r.status_code >= 400:
                 print(f"[ERROR] Upload certificate failed: {r.status_code} {r.text}")
        except Exception as e:
            print(f"[ERROR] Upload certificate exception: {e}")

