#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.env}"
# SECRETS_FILE="${2:-$ROOT_DIR/.env.secrets}"
VAULT_SECRETS_FILE="${3:-$ROOT_DIR/secrets/vault.secrets}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi


if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required but not found in PATH" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required but not found in PATH" >&2
  exit 1
fi

mkdir -p "$(dirname "$VAULT_SECRETS_FILE")"
touch "$VAULT_SECRETS_FILE"

upsert_env() {
  local file="$1"
  local key="$2"
  local value="$3"

  touch "$file"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
    rm -f "$file.bak"
  else
    printf "%s=%s\n" "$key" "$value" >> "$file"
  fi
}

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
# shellcheck disable=SC1090
source "$VAULT_SECRETS_FILE"
set +a

NAMESPACE="${K8S_NAMESPACE:-default}"
APPLICATION_NAME="${APPLICATION:-edc-connector}"
CONNECTOR_INSTANCE_ID="${CONNECTOR_ID:-connector}"
VAULT_INSTANCE="${IDENTITY_HUB_VAULT_INSTANCE:-${CONNECTOR_INSTANCE_ID}-ih}"
VAULT_STS_NAME="${VAULT_STATEFULSET_NAME:-${APPLICATION_NAME}-vault-${VAULT_INSTANCE}}"
VAULT_POD_NAME="${VAULT_STS_NAME}-0"
VAULT_ADDR_LOCAL="http://127.0.0.1:8200"

echo "Using namespace: ${NAMESPACE}"
echo "Using Vault StatefulSet: ${VAULT_STS_NAME}"

kubectl -n "$NAMESPACE" wait --for=condition=Ready "pod/${VAULT_POD_NAME}" --timeout=240s >/dev/null

vault_exec() {
  local cmd="$1"
  kubectl -n "$NAMESPACE" exec "$VAULT_POD_NAME" -- sh -lc "$cmd"
}

status_json="$(vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} vault status -format=json" 2>/dev/null || true)"
if [[ -z "$status_json" ]]; then
  echo "Could not read Vault status from pod ${VAULT_POD_NAME}" >&2
  exit 1
fi

initialized="$(echo "$status_json" | jq -r '.initialized')"
sealed="$(echo "$status_json" | jq -r '.sealed')"

if [[ "$initialized" != "true" ]]; then
  echo "Vault is not initialized, running init"
  init_json="$(vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} vault operator init -key-shares=1 -key-threshold=1 -format=json")"
  VAULT_UNSEAL_KEY="$(echo "$init_json" | jq -r '.unseal_keys_b64[0]')"
  VAULT_ROOT_TOKEN="$(echo "$init_json" | jq -r '.root_token')"

  if [[ -z "$VAULT_UNSEAL_KEY" || -z "$VAULT_ROOT_TOKEN" || "$VAULT_UNSEAL_KEY" == "null" || "$VAULT_ROOT_TOKEN" == "null" ]]; then
    echo "Vault init failed: ${init_json}" >&2
    exit 1
  fi

  upsert_env "$VAULT_SECRETS_FILE" "VAULT_UNSEAL_KEY" "$VAULT_UNSEAL_KEY"
  upsert_env "$VAULT_SECRETS_FILE" "VAULT_ROOT_TOKEN" "$VAULT_ROOT_TOKEN"
  sealed="true"
fi

if [[ -z "${VAULT_UNSEAL_KEY:-}" || -z "${VAULT_ROOT_TOKEN:-}" ]]; then
  echo "VAULT_UNSEAL_KEY or VAULT_ROOT_TOKEN is missing. Check $VAULT_SECRETS_FILE" >&2
  exit 1
fi

if [[ "$sealed" == "true" ]]; then
  echo "Vault is sealed, unsealing"
  vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} vault operator unseal '${VAULT_UNSEAL_KEY}' >/dev/null"
fi

mounts_json="$(vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} VAULT_TOKEN='${VAULT_ROOT_TOKEN}' vault secrets list -format=json")"
if ! echo "$mounts_json" | jq -e 'has("secret/")' >/dev/null; then
  vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} VAULT_TOKEN='${VAULT_ROOT_TOKEN}' vault secrets enable -path=secret kv-v2 >/dev/null"
  echo "Enabled KV v2 at secret/"
fi

vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} VAULT_TOKEN='${VAULT_ROOT_TOKEN}' vault secrets list -format=json >/dev/null"

vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} VAULT_TOKEN='${VAULT_ROOT_TOKEN}' vault policy write edc-runtime - <<'EOF' >/dev/null
path \"secret/data/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"delete\", \"list\"]
}

path \"secret/metadata/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"delete\", \"list\"]
}

path \"transit/keys/*\" {
  capabilities = [\"read\", \"list\"]
}

path \"transit/sign/*\" {
  capabilities = [\"update\"]
}

path \"transit/verify/*\" {
  capabilities = [\"update\"]
}

path \"transit/keys/issuer-*\" {
  capabilities = [\"create\", \"update\", \"read\", \"list\"]
}

path \"secret/data/public-keys/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"list\"]
}

path \"secret/metadata/public-keys/*\" {
  capabilities = [\"read\", \"list\", \"delete\"]
}

path \"secret/data/vc-metadata/*\" {
  capabilities = [\"create\", \"read\", \"update\", \"list\"]
}
EOF"

service_token_json="$(vault_exec "VAULT_ADDR=${VAULT_ADDR_LOCAL} VAULT_TOKEN='${VAULT_ROOT_TOKEN}' vault token create -policy=edc-runtime -orphan -format=json")"
VAULT_SERVICE_TOKEN="$(echo "$service_token_json" | jq -r '.auth.client_token')"
if [[ -z "$VAULT_SERVICE_TOKEN" || "$VAULT_SERVICE_TOKEN" == "null" ]]; then
  echo "Failed to create Vault service token: ${service_token_json}" >&2
  exit 1
fi

upsert_env "$VAULT_SECRETS_FILE" "VAULT_UNSEAL_KEY" "$VAULT_UNSEAL_KEY"
upsert_env "$VAULT_SECRETS_FILE" "VAULT_ROOT_TOKEN" "$VAULT_ROOT_TOKEN"
upsert_env "$VAULT_SECRETS_FILE" "VAULT_SERVICE_TOKEN" "$VAULT_SERVICE_TOKEN"

patch_payload="$(jq -cn --arg token "$VAULT_SERVICE_TOKEN" '{stringData: {EDC_VAULT_HASHICORP_TOKEN: $token}}')"

if kubectl -n "$NAMESPACE" get secret connector-secret >/dev/null 2>&1; then
  kubectl -n "$NAMESPACE" patch secret connector-secret --type merge -p "$patch_payload" >/dev/null
  echo "Patched connector-secret with generated Vault token"
fi

if kubectl -n "$NAMESPACE" get secret identity-hub-secret >/dev/null 2>&1; then
  kubectl -n "$NAMESPACE" patch secret identity-hub-secret --type merge -p "$patch_payload" >/dev/null
  echo "Patched identity-hub-secret with generated Vault token"
fi

if kubectl -n "$NAMESPACE" get deploy "${APPLICATION_NAME}-connector" >/dev/null 2>&1; then
  kubectl -n "$NAMESPACE" rollout restart "deploy/${APPLICATION_NAME}-connector" >/dev/null
fi

if kubectl -n "$NAMESPACE" get deploy "${APPLICATION_NAME}-identity-hub" >/dev/null 2>&1; then
  kubectl -n "$NAMESPACE" rollout restart "deploy/${APPLICATION_NAME}-identity-hub" >/dev/null
fi

echo "Vault is initialized and unsealed."
echo "Generated values stored in: $VAULT_SECRETS_FILE"
echo "Vault service token propagated to connector/identity-hub Kubernetes secrets."