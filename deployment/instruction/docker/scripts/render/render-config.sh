#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.env}"
SECRETS_FILE="${2:-$ROOT_DIR/.env.secrets}"
SECRETS_DIR="$ROOT_DIR/secrets"
OUT_DIR="$ROOT_DIR/.generated/config"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
if [[ -f "$SECRETS_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$SECRETS_FILE"
fi

if [[ -d "$SECRETS_DIR" ]]; then
  shopt -s nullglob
  for env_file in "$SECRETS_DIR"/*.env; do
    # shellcheck source=/dev/null
    source "$env_file"
  done
  shopt -u nullglob
fi
set +a

: "${CONNECTOR_DB_NAME:?CONNECTOR_DB_NAME is required}"
: "${CONNECTOR_DB_USER:?CONNECTOR_DB_USER is required}"
: "${CONNECTOR_DB_PASSWORD:?CONNECTOR_DB_PASSWORD is required}"
: "${PARTICIPANT_ID:?PARTICIPANT_ID is required}"
: "${CONNECTOR_PUBLIC_KEY_ID:?CONNECTOR_PUBLIC_KEY_ID is required}"
: "${CONNECTOR_STS_CLIENT_SECRET_ALIAS:?CONNECTOR_STS_CLIENT_SECRET_ALIAS is required}"
: "${PUBLIC_SCHEME:?PUBLIC_SCHEME is required}"
: "${CONNECTOR_HOST:?CONNECTOR_HOST is required}"
: "${CONNECTOR_ID:?CONNECTOR_ID is required}"
: "${KEYCLOAK_ADDRESS:?KEYCLOAK_ADDRESS is required}"
: "${IDENTITY_HUB_ADDRESS:?IDENTITY_HUB_ADDRESS is required}"
: "${FEDERATED_CATALOG_ADDRESS:?FEDERATED_CATALOG_ADDRESS is required}"
: "${ISSUER_DID:?ISSUER_DID is required}"
: "${CATALOG_DSP_ID:?CATALOG_DSP_ID is required}"
: "${CATALOG_API_KEY:?CATALOG_API_KEY is required}"
: "${CONNECTOR_API_KEY:?CONNECTOR_API_KEY is required}"
: "${IDENTITY_HUB_HOST:?IDENTITY_HUB_HOST is required}"
: "${IDENTITY_HUB_DB_NAME:?IDENTITY_HUB_DB_NAME is required}"
: "${IDENTITY_HUB_DB_USER:?IDENTITY_HUB_DB_USER is required}"
: "${IDENTITY_HUB_DB_PASSWORD:?IDENTITY_HUB_DB_PASSWORD is required}"
: "${IDENTITY_HUB_STS_PUBLIC_KEY_ID:?IDENTITY_HUB_STS_PUBLIC_KEY_ID is required}"
: "${IDENTITY_HUB_SUPERUSER_KEY:?IDENTITY_HUB_SUPERUSER_KEY is required}"
: "${VAULT_ADDRESS:?VAULT_ADDRESS is required}"

# Normalize base URLs to avoid generating invalid doubled paths (for example /api/api/...).
KEYCLOAK_ADDRESS="${KEYCLOAK_ADDRESS%/}"
IDENTITY_HUB_ADDRESS="${IDENTITY_HUB_ADDRESS%/}"
VAULT_ADDRESS="${VAULT_ADDRESS%/}"
FEDERATED_CATALOG_ADDRESS="${FEDERATED_CATALOG_ADDRESS%/}"
FEDERATED_CATALOG_ADDRESS="${FEDERATED_CATALOG_ADDRESS%/api}"

VAULT_SERVICE_TOKEN="${VAULT_SERVICE_TOKEN:-dev-token}"

mkdir -p "$OUT_DIR"

render_file() {
  local template_file="$1"
  local output_file="$2"

  awk \
    -v CONNECTOR_DB_NAME="$CONNECTOR_DB_NAME" \
    -v CONNECTOR_DB_USER="$CONNECTOR_DB_USER" \
    -v CONNECTOR_DB_PASSWORD="$CONNECTOR_DB_PASSWORD" \
    -v PARTICIPANT_ID="$PARTICIPANT_ID" \
    -v CONNECTOR_PUBLIC_KEY_ID="$CONNECTOR_PUBLIC_KEY_ID" \
    -v CONNECTOR_STS_CLIENT_SECRET_ALIAS="$CONNECTOR_STS_CLIENT_SECRET_ALIAS" \
    -v PUBLIC_SCHEME="$PUBLIC_SCHEME" \
    -v CONNECTOR_HOST="$CONNECTOR_HOST" \
    -v CONNECTOR_ID="$CONNECTOR_ID" \
    -v KEYCLOAK_ADDRESS="$KEYCLOAK_ADDRESS" \
    -v IDENTITY_HUB_ADDRESS="$IDENTITY_HUB_ADDRESS" \
    -v FEDERATED_CATALOG_ADDRESS="$FEDERATED_CATALOG_ADDRESS" \
    -v ISSUER_DID="$ISSUER_DID" \
    -v CATALOG_DSP_ID="$CATALOG_DSP_ID" \
    -v CATALOG_API_KEY="$CATALOG_API_KEY" \
    -v CONNECTOR_API_KEY="$CONNECTOR_API_KEY" \
    -v VAULT_SERVICE_TOKEN="$VAULT_SERVICE_TOKEN" \
    -v IDENTITY_HUB_HOST="$IDENTITY_HUB_HOST" \
    -v IDENTITY_HUB_DB_NAME="$IDENTITY_HUB_DB_NAME" \
    -v IDENTITY_HUB_DB_USER="$IDENTITY_HUB_DB_USER" \
    -v IDENTITY_HUB_DB_PASSWORD="$IDENTITY_HUB_DB_PASSWORD" \
    -v IDENTITY_HUB_STS_PUBLIC_KEY_ID="$IDENTITY_HUB_STS_PUBLIC_KEY_ID" \
    -v IDENTITY_HUB_SUPERUSER_KEY="$IDENTITY_HUB_SUPERUSER_KEY" \
    -v VAULT_ADDRESS="$VAULT_ADDRESS" \
    '{
      gsub(/__CONNECTOR_DB_NAME__/, CONNECTOR_DB_NAME)
      gsub(/__CONNECTOR_DB_USER__/, CONNECTOR_DB_USER)
      gsub(/__CONNECTOR_DB_PASSWORD__/, CONNECTOR_DB_PASSWORD)
      gsub(/__PARTICIPANT_ID__/, PARTICIPANT_ID)
      gsub(/__CONNECTOR_PUBLIC_KEY_ID__/, CONNECTOR_PUBLIC_KEY_ID)
      gsub(/__CONNECTOR_STS_CLIENT_SECRET_ALIAS__/, CONNECTOR_STS_CLIENT_SECRET_ALIAS)
      gsub(/__PUBLIC_SCHEME__/, PUBLIC_SCHEME)
      gsub(/__CONNECTOR_HOST__/, CONNECTOR_HOST)
      gsub(/__CONNECTOR_ID__/, CONNECTOR_ID)
      gsub(/__KEYCLOAK_ADDRESS__/, KEYCLOAK_ADDRESS)
      gsub(/__IDENTITY_HUB_ADDRESS__/, IDENTITY_HUB_ADDRESS)
      gsub(/__FEDERATED_CATALOG_ADDRESS__/, FEDERATED_CATALOG_ADDRESS)
      gsub(/__ISSUER_DID__/, ISSUER_DID)
      gsub(/__CATALOG_DSP_ID__/, CATALOG_DSP_ID)
      gsub(/__CATALOG_API_KEY__/, CATALOG_API_KEY)
      gsub(/__CONNECTOR_API_KEY__/, CONNECTOR_API_KEY)
      gsub(/__VAULT_SERVICE_TOKEN__/, VAULT_SERVICE_TOKEN)
      gsub(/__IDENTITY_HUB_HOST__/, IDENTITY_HUB_HOST)
      gsub(/__IDENTITY_HUB_DB_NAME__/, IDENTITY_HUB_DB_NAME)
      gsub(/__IDENTITY_HUB_DB_USER__/, IDENTITY_HUB_DB_USER)
      gsub(/__IDENTITY_HUB_DB_PASSWORD__/, IDENTITY_HUB_DB_PASSWORD)
      gsub(/__IDENTITY_HUB_STS_PUBLIC_KEY_ID__/, IDENTITY_HUB_STS_PUBLIC_KEY_ID)
      gsub(/__IDENTITY_HUB_SUPERUSER_KEY__/, IDENTITY_HUB_SUPERUSER_KEY)
      gsub(/__VAULT_ADDRESS__/, VAULT_ADDRESS)
      print
    }' "$template_file" > "$output_file"

  if grep -qE '__[A-Z0-9_]+__' "$output_file"; then
    echo "Unresolved placeholders left in $output_file" >&2
    grep -oE '__[A-Z0-9_]+__' "$output_file" | sort -u >&2
    exit 1
  fi
}

mkdir -p "$OUT_DIR"

echo "Rendering connector.properties..."
render_file "$ROOT_DIR/config/templates/connector.properties.template" "$OUT_DIR/connector.properties"

echo "Rendering identity-hub.properties..."
render_file "$ROOT_DIR/config/templates/identity-hub.properties.template" "$OUT_DIR/identity-hub.properties"

echo "Rendered files to: $OUT_DIR"
