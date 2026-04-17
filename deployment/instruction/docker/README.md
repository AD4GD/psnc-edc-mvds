# Docker Deployment Guide

This is the only deployment instruction you need for this folder.
It covers the full flow using:

- `docker-compose.yaml`
- `.env`
- `.env.secrets`

## Introduction

This guide covers deployment and bootstrap of Data Space participant services on Linux hosts.
Recommended platform is Linux on amd64/x86_64 architecture. It does not cover VM provisioning itself, only service deployment and configuration.

## 1. Requirements

#### 1.1. Operating system and architecture

- Linux (recommended: Ubuntu 24.04+ or equivalent)
- amd64 / x86_64 CPU architecture

#### 1.2. Minimum host resources

- CPU: 4 vCPU (recommended 8 vCPU)
- RAM: 12 GB (recommended 16 GB)
- Storage: 50 GB free disk ( recommended 80 GB for logs/images growth)

#### 1.3. Tools

- Docker + Docker Compose v2
- `make`
- `openssl`
- `htpasswd` (from apache2-utils / httpd-tools)
- Python 3
- `pip` (for Python dependencies used by Keycloak bootstrap scripts)

## 2. Initialize config files

```bash
make init
```

This creates:

- `.env` from `.env.example`
- `.env.secrets` from `.env.secrets.example`

Install Python dependencies for Keycloak bootstrap scripts:

```bash
make python-deps
```

## 3. Generate credentials in terminal and paste into `.env`

### 3.1 Generate strong passwords

Use this command each time you need a new random value:

```bash
openssl rand -base64 32 | head -c 32; echo
```

Generate values and paste them into `.env`, for example:

- `COMMON_DB_PASSWORD`
- `CONNECTOR_DB_PASSWORD`
- `KEYCLOAK_DB_PASSWORD`
- `KEYCLOAK_ADMIN_PASSWORD`
- `IDENTITY_HUB_DB_PASSWORD`
- `STORAGE_SECRET_KEY`
- `CONNECTOR_STS_CLIENT_SECRET_ALIAS`

For `IDENTITY_HUB_SUPERUSER_KEY`, generate value in format `base64(username).base64(secret)` with:

```bash
IH_USER="super-user"; IH_SECRET="super-secret-key"; printf "%s.%s\n" "$(printf '%s' "$IH_USER" | base64 | tr -d '\n')" "$(printf '%s' "$IH_SECRET" | base64 | tr -d '\n')"
```

For random secret (recommended), use:

```bash
IH_USER="super-user"; IH_SECRET="$(openssl rand -base64 32 | tr -d '\n')"
printf "%s.%s\n" "$(printf '%s' "$IH_USER" | base64 | tr -d '\n')" "$(printf '%s' "$IH_SECRET" | base64 | tr -d '\n')"
```

### 3.2 Generate Traefik basic auth value

1. Generate a random password and save it temporarily:

```bash
TRAEFIK_PASS="$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 20)"; echo "$TRAEFIK_PASS"
```

2. Generate the value for `TRAEFIK_BASIC_AUTH`:

```bash
htpasswd -nb admin "$TRAEFIK_PASS" | sed -e 's/\$/\$\$/g'
```

3. Copy output (format: `admin:$$apr1$$...`) into `.env` as:

- `TRAEFIK_BASIC_AUTH=...`

## 4. Fill `.env` required settings

#### 4.1 Profiles

First thing is to decide what services you want to select. There are 4 possible profiles
- `connector` (mandatory). Consists of connector + db + dashboard
- `keycloak` (optional). Consists of keycloak + db
- `identity` (optional). Consists of identity hub + db + key vault
- `storage` (optional). Consists of consumer backend + storage

Examples:

- Mandatory services only:

```env
COMPOSE_PROFILES=
```

- Enable Keycloak + Identity + Storage:

```env
COMPOSE_PROFILES=keycloak,identity,storage
```
#### 4.2 Provided by a dataspace

Important placeholders to replace with real Data Space values:

- `ISSUER_DID`
- `FEDERATED_CATALOG_ADDRESS`
- `DATASPACE_HUB_URL`
- `CATALOG_API_KEY`

#### 4.3 Base configuration
At minimum, verify and set:

- Hosts:
  - `CONNECTOR_HOST`
  - `DASHBOARD_HOST`
  - `KEYCLOAK_HOST`
  - `TRAEFIK_DASHBOARD_HOST`
  - `IDENTITY_HUB_HOST`
  - `VAULT_HOST`
  - `CONSUMER_BACKEND_HOST`
  - `STORAGE_HOST`
- URLs (fill in only if you are NOT deploying these):
  - `KEYCLOAK_ADDRESS`
  - `IDENTITY_HUB_ADDRESS`
  - `VAULT_ADDRESS`
- Identity:
  - `CONNECTOR_ID`
  - `PARTICIPANT_ID` - automatically generated


Do not keep placeholders from `.env.example` in production. These two values must be provided by Data Space owners.

## 5. Render generated configuration

```bash
make render
```

This creates:

- `.generated/config/connector.properties`
- `.generated/config/identity-hub.properties`
- `.generated/config/dashboard/nginx.conf`
- `.generated/config/dashboard/app.config.json`

## 6. Prepare ACME file for TLS certificates

```bash
touch acme.json && chmod 600 acme.json
```

## 7. (Optional, but required if `identity` profile is enabled) initialize Vault

```bash
make vault-init
```

This script:

- starts `key-vault`
- initializes and unseals Vault
- writes `VAULT_UNSEAL_KEY`, `VAULT_ROOT_TOKEN`, and one shared `VAULT_SERVICE_TOKEN` to `.env.secrets`
- writes snapshot to `secrets/vault.env`
- prints and checks `${VAULT_ADDRESS}/v1/sys/health` (if `VAULT_ADDRESS` is set)

Token model in this deployment:

- `VAULT_UNSEAL_KEY`: only for `vault operator unseal`
- `VAULT_ROOT_TOKEN`: admin token used by init script to configure Vault
- `VAULT_SERVICE_TOKEN`: one runtime token used by both Connector and Identity Hub

## 8. Start deployment

Use profiles from `.env`:

```bash
make up
```

Or override profiles once from CLI:

```bash
make PROFILES="identity" up
make PROFILES="keycloak identity storage" up
```

Note: if `identity` is enabled, `make up` automatically runs Vault init/unseal first to unseal the key-vault.

## 8.1 Configure Keycloak bootstrap entities

After services are up (especially when `keycloak` profile is enabled), run:

```bash
make configure-keycloak-full
```

This runs:

- participant bootstrap (`configure_participant.py`)
- connector bootstrap (`participant_ensure_connector.py`)

Both scripts read configuration from system environment variables exported from `.env` and `.env.secrets` by Makefile.

## 8.2 Bootstrap and verify full dataspace

Config for these scripts is auto-rendered from `.env` and `.env.secrets` into:

- `.generated/dataspace-config`

Initialize dataspace (Identity Hub context + connector secret + VC issuance):

```bash
make init-dataspace
```

Useful variants:

```bash
make init-dataspace SKIP_VC=true
make init-dataspace PARTICIPANT=participant
```

Verify dataspace state using the same config directory:

```bash
make verify-dataspace
```

Verbose verification output:

```bash
make verify-dataspace VERIFY_VERBOSE=true
```

If needed, you can still point scripts to a custom config dir:

```bash
make init-dataspace DATASPACE_CONFIG_DIR=./scripts/configure/config
make verify-dataspace DATASPACE_CONFIG_DIR=./scripts/configure/config
```

## 9. Verify deployment

```bash
make ps
make logs SERVICE=connector
```

Useful checks:

- Connector: `https://<CONNECTOR_HOST>/api`
- Dashboard: `https://<DASHBOARD_HOST>`
- Vault health: `${VAULT_ADDRESS}/v1/sys/health`

## 10. Stop or clean up

Stop services:

```bash
make down
```

Stop and remove volumes (destructive):

```bash
make clean
```