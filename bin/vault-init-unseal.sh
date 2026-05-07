#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/vaults.json" ]]; then
    DEFAULT_VAULTS_CONFIG_FILE="$SCRIPT_DIR/vaults.json"
else
    DEFAULT_VAULTS_CONFIG_FILE="$SCRIPT_DIR/../compose/vaults.json"
fi
readonly VAULTS_CONFIG_FILE="${VAULTS_CONFIG_FILE:-$DEFAULT_VAULTS_CONFIG_FILE}"

# ----- Functions ----- #

vault_ready() {
    local addr="$1"
    curl -s -f -o /dev/null "$addr/v1/sys/seal-status" 2>/dev/null
}

seal_status() {
    local addr="$1"
    local res
    res=$(curl -s "$addr/v1/sys/seal-status")
    jq -r '[.initialized, .sealed] | @tsv' <<< "$res"
}

get_env_value() {
    local env_file="$1"
    local env_key="$2"

    grep "^${env_key}=" "$env_file" | cut -d'=' -f2- | sed 's/ *$//'
}

resolve_addr() {
    local address_env="$1"
    local default_addr="$2"

    if [[ -n "$address_env" && -n "${!address_env:-}" ]]; then
        echo "${!address_env}"
    else
        echo "$default_addr"
    fi
}

normalize_env_file_path() {
    local env_file="$1"

    if [[ "$env_file" = /* ]]; then
        echo "$env_file"
    else
        echo "$SCRIPT_DIR/$env_file"
    fi
}

validate_config() {
    if [[ ! -f "$VAULTS_CONFIG_FILE" ]]; then
        echo "Error: Vault configuration file not found: $VAULTS_CONFIG_FILE" >&2
        exit 1
    fi

    if ! jq -e '
      .vaults and
      (.vaults | type == "array") and
      (.vaults | length > 0) and
      all(.vaults[];
        (.name | type == "string" and length > 0) and
        (.defaultAddr | type == "string" and length > 0) and
        (.envFile | type == "string" and length > 0) and
        (.tokenEnv | type == "string" and length > 0) and
        (.shardEnv | type == "string" and length > 0)
      )
    ' "$VAULTS_CONFIG_FILE" >/dev/null; then
        echo "Error: invalid JSON format in $VAULTS_CONFIG_FILE" >&2
        exit 1
    fi
}

ensure_secret_engine() {
    local name="$1"
    local addr="$2"
    local env_file="$3"
    local token_env="$4"

    local token
    token=$(get_env_value "$env_file" "$token_env")

    if [ -z "$token" ] || [ "$token" = "null" ]; then
        echo "Error: missing token ${token_env} in $env_file (cannot create secret/ engine)" >&2
        exit 1
    fi

    local mounts_resp
    mounts_resp=$(curl -s -X GET "$addr/v1/sys/mounts" -H "X-Vault-Token: $token")

    if echo "$mounts_resp" | jq -e '."secret/"' >/dev/null 2>&1; then
        echo "Vault $name: secret/ engine already exists." >&2
        return 0
    fi

    local create_resp
    create_resp=$(curl -s -X POST "$addr/v1/sys/mounts/secret" \
        -H "X-Vault-Token: $token" \
        -H "Content-Type: application/json" \
        -d '{"type":"kv","options":{"version":"2"}}')

    if [ -n "$create_resp" ] && [ "$create_resp" != "null" ]; then
        echo "Error creating secret/ engine for Vault $name" >&2
        echo "$create_resp" >&2
        exit 1
    fi

    echo "Vault $name: KV engine created at path secret/." >&2
}

vault_init() {
    local name="$1"
    local addr="$2"
    local env_file="$3"
    local token_env="$4"
    local shard_env="$5"

    echo "Vault $name is not initialized; initializing..." >&2

    local init_resp
    init_resp=$(curl -s -X PUT "$addr/v1/sys/init" \
        -H "Content-Type: application/json" \
        -d '{
            "secret_shares": 1,
            "secret_threshold": 1
        }')

    # --- Parse init response fields ---
    local token shard
    token=$(echo "$init_resp" | jq -r '.root_token')
    shard=$(echo "$init_resp" | jq -r '.keys_base64[0]')

    # --- Validate: token and unseal key must be present ---
    if [ -z "$token" ] || [ "$token" = "null" ] || [ -z "$shard" ] || [ "$shard" = "null" ]; then
        echo "Init response parse error: missing root_token or keys_base64" >&2
        echo "$init_resp" >&2
        exit 1
    fi

    # --- Create destination directory and file ---
    mkdir -p "$(dirname "$env_file")"

    cat > "$env_file" << EOF
${token_env}=$token
${shard_env}=$shard
EOF

    echo "Saved Vault $name keys to $env_file" >&2
}

vault_unseal() {
    local name="$1"
    local addr="$2"
    local env_file="$3"
    local shard_env="$4"

    echo "Vault $name at $addr is sealed; unsealing..." >&2

    if [ ! -f "$env_file" ]; then
        echo "Error: file $env_file does not exist" >&2
        exit 1
    fi

    local shard_var
    shard_var=$(grep "^${shard_env}=" "$env_file" | cut -d'=' -f2- | sed 's/ *$//')

    if [ -z "$shard_var" ] || [ "$shard_var" = "null" ]; then
        echo "Error: missing key ${shard_env} in $env_file" >&2
        exit 1
    fi

    curl -s -X POST "$addr/v1/sys/unseal" \
        -H "Content-Type: application/json" \
        -d "{\"key\":\"$shard_var\"}" >/dev/null

    echo "Vault $name unsealed" >&2
}

init_unseal() {
    local name="$1"
    local addr="$2"
    local env_file="$3"
    local token_env="$4"
    local shard_env="$5"

    echo "Processing Vault $name at $addr -> $env_file" >&2

    local retries=30
    local delay=2
    for ((i=0; i<retries; i++)); do
        if vault_ready "$addr"; then
            echo "Vault $name is reachable." >&2
            break
        fi
        sleep "$delay"
    done

    if ! vault_ready "$addr"; then
        echo "Vault $name unavailable after $retries attempts" >&2
        exit 1
    fi

    read -r INIT SEALED < <(seal_status "$addr")

    if [ "$INIT" == "false" ]; then
        # Mode INIT: saving keys to env file and unsealing immediately
        vault_init "$name" "$addr" "$env_file" "$token_env" "$shard_env"
        vault_unseal "$name" "$addr" "$env_file" "$shard_env"
        ensure_secret_engine "$name" "$addr" "$env_file" "$token_env"
    elif [ "$SEALED" == "true" ]; then
        # Mode UNSEAL: read from env & unseal
        vault_unseal "$name" "$addr" "$env_file" "$shard_env"
    else
        echo "Vault $name is initialized and already unsealed." >&2
    fi
}

# ----- Main script flow -----
validate_config

while IFS=$'\t' read -r NAME ADDRESS_ENV DEFAULT_ADDR ENV_FILE TOKEN_ENV SHARD_ENV; do
        ADDR="$(resolve_addr "$ADDRESS_ENV" "$DEFAULT_ADDR")"
        RESOLVED_ENV_FILE="$(normalize_env_file_path "$ENV_FILE")"
        init_unseal "$NAME" "$ADDR" "$RESOLVED_ENV_FILE" "$TOKEN_ENV" "$SHARD_ENV"
done < <(
        jq -r '.vaults[]
            | select(.enabled != false)
            | [
                    .name,
                    (.addressEnv // ""),
                    .defaultAddr,
                    .envFile,
                    .tokenEnv,
                    .shardEnv
                ]
            | @tsv' "$VAULTS_CONFIG_FILE"
)

echo "Done: all Vaults are initialized and unsealed." >&2
