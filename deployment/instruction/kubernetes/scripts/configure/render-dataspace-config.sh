#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env}"
# SECRETS_FILE="${2:-.env.secrets}"
OUT_DIR="${3:-./.generated/dataspace-config}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] Missing env file: $ENV_FILE" >&2
  exit 1
fi

# if [[ ! -f "$SECRETS_FILE" ]]; then
#   echo "[ERROR] Missing secrets file: $SECRETS_FILE" >&2
#   exit 1
# fi

load_dotenv_file() {
  local file="$1"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]] && continue

    if [[ "$line" != *"="* ]]; then
      continue
    fi

    local key="${line%%=*}"
    local value="${line#*=}"

    key="$(echo "$key" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    value="$(echo "$value" | sed -e 's/[[:space:]]#.*$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

    if [[ "$value" =~ ^".*"$ ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "$value" =~ ^'.*'$ ]]; then
      value="${value:1:${#value}-2}"
    fi

    export "$key=$value"
  done < "$file"
}

normalize_string_value() {
  local value="$1"

  # Unescape wrapped quotes and trim any repeated surrounding quotes.
  value="${value//\\\"/\"}"
  while [[ -n "$value" && ( "${value:0:1}" == '"' || "${value:0:1}" == "'" ) ]]; do
    value="${value:1}"
  done
  while [[ -n "$value" && ( "${value: -1}" == '"' || "${value: -1}" == "'" ) ]]; do
    value="${value::-1}"
  done

  echo "$value"
}

normalize_int_value() {
  local value="$1"
  local fallback="$2"
  value="$(normalize_string_value "$value")"
  if [[ "$value" =~ ^[0-9]+$ ]]; then
    echo "$value"
  else
    echo "$fallback"
  fi
}

load_dotenv_file "$ENV_FILE"
# load_dotenv_file "$SECRETS_FILE"

PUBLIC_SCHEME="${PUBLIC_SCHEME:-https}"
CONNECTOR_HOST="${CONNECTOR_HOST:-connector.example.com}"
IDENTITY_HUB_HOST="${IDENTITY_HUB_HOST:-identity-hub.example.com}"
VAULT_HOST="${VAULT_HOST:-vault.example.com}"
CONNECTOR_ID="${CONNECTOR_ID:-test-connector}"

IDENTITY_HUB_ADDRESS="${IDENTITY_HUB_ADDRESS:-${PUBLIC_SCHEME}://${IDENTITY_HUB_HOST}}"
if [[ -z "$IDENTITY_HUB_ADDRESS" || "$IDENTITY_HUB_ADDRESS" == *'${'* ]]; then
  IDENTITY_HUB_ADDRESS="${PUBLIC_SCHEME}://${IDENTITY_HUB_HOST}"
fi

VAULT_ADDRESS="${VAULT_ADDRESS:-${PUBLIC_SCHEME}://${VAULT_HOST}}"
if [[ -z "$VAULT_ADDRESS" || "$VAULT_ADDRESS" == *'${'* ]]; then
  VAULT_ADDRESS="${PUBLIC_SCHEME}://${VAULT_HOST}"
fi

PARTICIPANT_ID="${PARTICIPANT_ID:-did:web:${IDENTITY_HUB_HOST}:${CONNECTOR_ID}}"
if [[ -z "$PARTICIPANT_ID" || "$PARTICIPANT_ID" == *'${'* ]]; then
  PARTICIPANT_ID="did:web:${IDENTITY_HUB_HOST}:${CONNECTOR_ID}"
fi
CONNECTOR_STS_CLIENT_SECRET_ALIAS="${CONNECTOR_STS_CLIENT_SECRET_ALIAS:-sts-client-secret}"
CONNECTOR_API_KEY="${CONNECTOR_API_KEY:-edc}"
IDENTITY_HUB_SUPERUSER_KEY="${IDENTITY_HUB_SUPERUSER_KEY:-CHANGE_ME_IDENTITY_HUB_SUPERUSER_KEY}"
DATASPACE_HUB_URL="${DATASPACE_HUB_URL:-${DATA_SPACE_HUB_URL:-CHANGE_ME_DATASPACE_HUB_URL}}"
DSH_API_KEY="${DSH_API_KEY:-}"
DATASPACE_MAX_WAIT_SECONDS="${DATASPACE_MAX_WAIT_SECONDS:-120}"
DATASPACE_POLL_INTERVAL_SECONDS="${DATASPACE_POLL_INTERVAL_SECONDS:-3}"

PARTICIPANT_ID="$(normalize_string_value "$PARTICIPANT_ID")"
CONNECTOR_STS_CLIENT_SECRET_ALIAS="$(normalize_string_value "$CONNECTOR_STS_CLIENT_SECRET_ALIAS")"
IDENTITY_HUB_ADDRESS="$(normalize_string_value "$IDENTITY_HUB_ADDRESS")"
IDENTITY_HUB_SUPERUSER_KEY="$(normalize_string_value "$IDENTITY_HUB_SUPERUSER_KEY")"
VAULT_ADDRESS="$(normalize_string_value "$VAULT_ADDRESS")"
CONNECTOR_API_KEY="$(normalize_string_value "$CONNECTOR_API_KEY")"
DATASPACE_HUB_URL="$(normalize_string_value "$DATASPACE_HUB_URL")"
DSH_API_KEY="$(normalize_string_value "$DSH_API_KEY")"
PUBLIC_SCHEME="$(normalize_string_value "$PUBLIC_SCHEME")"
CONNECTOR_HOST="$(normalize_string_value "$CONNECTOR_HOST")"
DATASPACE_MAX_WAIT_SECONDS="$(normalize_int_value "$DATASPACE_MAX_WAIT_SECONDS" "120")"
DATASPACE_POLL_INTERVAL_SECONDS="$(normalize_int_value "$DATASPACE_POLL_INTERVAL_SECONDS" "3")"

mkdir -p "$OUT_DIR/participants"

jq -n \
  --arg url "$DATASPACE_HUB_URL" \
  --arg dsh_api_key "$DSH_API_KEY" \
  --argjson max_wait "$DATASPACE_MAX_WAIT_SECONDS" \
  --argjson poll_interval "$DATASPACE_POLL_INTERVAL_SECONDS" \
  '{
    data_space_hub: ({ url: $url } + (if ($dsh_api_key | length) > 0 then { api_key: $dsh_api_key } else {} end)),
    timeouts: {
      max_wait_seconds: $max_wait,
      poll_interval_seconds: $poll_interval
    }
  }' > "$OUT_DIR/dataspace.json"

jq -n \
  --arg did "$PARTICIPANT_ID" \
  --arg sts_alias "$CONNECTOR_STS_CLIENT_SECRET_ALIAS" \
  --arg ih_base "$IDENTITY_HUB_ADDRESS" \
  --arg ih_api_key "$IDENTITY_HUB_SUPERUSER_KEY" \
  --arg vault_addr "$VAULT_ADDRESS" \
  --arg connector_api_key "$CONNECTOR_API_KEY" \
  --arg connector_mgmt_url "${PUBLIC_SCHEME}://${CONNECTOR_HOST}/api/management" \
  --arg connector_dsp_url "${PUBLIC_SCHEME}://${CONNECTOR_HOST}/api/dsp" \
  '{
    did: $did,
    sts_client_secret_alias: $sts_alias,
    identity_hub: {
      base_url: $ih_base,
      identity_api_url: ($ih_base + "/api/identity"),
      credentials_api_url: ($ih_base + "/api/credentials"),
      api_key: $ih_api_key,
      vault_address: $vault_addr,
      public_key_pem_path: "certs/consumer_public.pem"
    },
    connector: {
      management_api_url: $connector_mgmt_url,
      api_key: $connector_api_key,
      dsp_url: $connector_dsp_url
    }
  }' > "$OUT_DIR/participants/participant.json"

if [[ -f "./scripts/configure/config/certs/consumer_public.pem" ]]; then
  mkdir -p "$OUT_DIR/certs"
  cp "./scripts/configure/config/certs/consumer_public.pem" "$OUT_DIR/certs/consumer_public.pem"
fi

echo "[INFO] Rendered dataspace config to: $OUT_DIR"
