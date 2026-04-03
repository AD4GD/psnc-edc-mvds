#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${1:-$ROOT_DIR/docker-compose.yaml}"
ENV_FILE="${2:-$ROOT_DIR/.env}"
SECRETS_FILE="${3:-$ROOT_DIR/.env.secrets}"
SECRETS_DIR="$ROOT_DIR/secrets"


if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

if [[ ! -f "$SECRETS_FILE" ]]; then
  cp "$ROOT_DIR/.env.secrets.example" "$SECRETS_FILE"
fi

mkdir -p "$SECRETS_DIR"

# Helper: update or insert env var in file
upsert_env() {
  local file="$1"
  local key="$2"
  local value="$3"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
    rm -f "$file.bak"
  else
    printf "%s=%s\n" "$key" "$value" >> "$file"
  fi
}



cd "$ROOT_DIR"

set -a
source "$ENV_FILE"
source "$SECRETS_FILE"
set +a


# Start Vault and Traefik containers if not running
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile identity up -d key-vault traefik

echo "Waiting for Vault API to become reachable..."
max_wait_seconds=120
sleep_seconds=2
elapsed=0
status_json=""

while true; do
  status_json="$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc 'vault status -format=json 2>/dev/null' 2>/dev/null || true)"
  if [[ -n "$status_json" ]]; then
    break
  fi
  if (( elapsed >= max_wait_seconds )); then
    echo "Vault API did not become reachable within ${max_wait_seconds}s" >&2
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps key-vault || true
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs --tail=120 key-vault || true
    exit 1
  fi
  sleep "$sleep_seconds"
  elapsed=$((elapsed + sleep_seconds))
done

# Use jq to parse status (no python)
initialized="$(echo "$status_json" | jq -r '.initialized')"
sealed="$(echo "$status_json" | jq -r '.sealed')"

if [[ "$initialized" != "true" ]]; then
  echo "Vault not initialized, running init..."
  init_json="$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc 'vault operator init -key-shares=1 -key-threshold=1 -format=json')"
  unseal_key="$(echo "$init_json" | jq -r '.unseal_keys_b64[0]')"
  root_token="$(echo "$init_json" | jq -r '.root_token')"
  if [[ -z "$unseal_key" || -z "$root_token" || "$unseal_key" == "null" || "$root_token" == "null" ]]; then
    echo "Vault init failed, response: $init_json" >&2
    exit 1
  fi
  upsert_env "$SECRETS_FILE" "VAULT_UNSEAL_KEY" "$unseal_key"
  upsert_env "$SECRETS_FILE" "VAULT_ROOT_TOKEN" "$root_token"
  echo "Vault initialized. Keys saved to $SECRETS_FILE"
  sealed="true"
fi

set -a
source "$SECRETS_FILE"
set +a

if [[ -z "${VAULT_UNSEAL_KEY:-}" || -z "${VAULT_ROOT_TOKEN:-}" ]]; then
  echo "VAULT_UNSEAL_KEY / VAULT_ROOT_TOKEN missing in $SECRETS_FILE" >&2
  exit 1
fi

if [[ "$sealed" == "true" ]]; then
  echo "Vault is sealed, unsealing..."
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc "vault operator unseal '$VAULT_UNSEAL_KEY' >/dev/null"
fi

# Login and create policy/token
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc "vault login '$VAULT_ROOT_TOKEN' >/dev/null"

# Ensure secret/ engine exists
mounts_json="$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc 'vault secrets list -format=json')"
if ! echo "$mounts_json" | jq -e 'has("secret/")' >/dev/null; then
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc "vault secrets enable -path=secret kv-v2 >/dev/null"
  echo "Enabled KV v2 at secret/"
fi

# Write policy
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc "vault policy write edc-service - <<'EOF' >/dev/null
path \"secret/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"delete\", \"list\"]
}
EOF"

# Create service token
service_token_json="$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T key-vault sh -lc 'vault token create -policy=edc-service -orphan -format=json')"
service_token="$(echo "$service_token_json" | jq -r '.auth.client_token')"
if [[ -z "$service_token" || "$service_token" == "null" ]]; then
  echo "Failed to create service token: $service_token_json" >&2
  exit 1
fi
upsert_env "$SECRETS_FILE" "VAULT_SERVICE_TOKEN" "$service_token"

set -a
source "$SECRETS_FILE"
set +a


echo "Vault is initialized and unsealed. Service token updated in $SECRETS_FILE"

# if [[ -n "${VAULT_ADDRESS:-}" ]]; then
#   echo "Vault external URL: ${VAULT_ADDRESS}"
#   external_health_status="$(curl -ks -o /dev/null -w "%{http_code}" "${VAULT_ADDRESS}/v1/sys/health" || true)"
#   echo "Vault health endpoint status: ${external_health_status:-n/a}"
#   if [[ "$external_health_status" =~ ^(200|429|472|473|501|503)$ ]]; then
#     echo "Vault external endpoint is reachable (HTTP ${external_health_status})"
#   else
#     echo "Warning: could not verify Vault external endpoint at ${VAULT_ADDRESS}/v1/sys/health (HTTP ${external_health_status:-n/a})" >&2
#   fi
# fi
# external_health_status="$(curl -ks --max-time 5 -w "%{http_code}" -o /tmp/vault_health_out.$$ "${VAULT_ADDRESS}/v1/sys/health" || true)"
# health_body="$(cat /tmp/vault_health_out.$$ 2>/dev/null || true)"
# rm -f /tmp/vault_health_out.$$
# if [[ "$external_health_status" =~ ^(200|429|472|473|501|503)$ ]]; then
#   echo "Vault external endpoint is reachable (HTTP ${external_health_status})"
# else
#   echo "Warning: could not verify Vault external endpoint at ${VAULT_ADDRESS}/v1/sys/health (HTTP ${external_health_status:-n/a})" >&2
#   echo "Response body: $health_body" >&2
# fi