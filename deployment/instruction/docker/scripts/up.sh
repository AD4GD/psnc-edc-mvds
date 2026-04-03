#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${1:-$ROOT_DIR/docker-compose.yaml}"
ENV_FILE="${2:-$ROOT_DIR/.env}"
SECRETS_FILE="${3:-$ROOT_DIR/.env.secrets}"
PROFILES_RAW="${4:-}"

profile_args=()
has_identity=false

if [[ -n "$PROFILES_RAW" ]]; then
  for profile in $PROFILES_RAW; do
    profile_args+=("--profile" "$profile")
    if [[ "$profile" == "identity" ]]; then
      has_identity=true
    fi
  done
fi

if [[ "$has_identity" == true ]]; then
  "$ROOT_DIR/scripts/vault-init-unseal.sh" "$COMPOSE_FILE" "$ENV_FILE" "$SECRETS_FILE"
fi

"$ROOT_DIR/scripts/render/render-config.sh" "$ENV_FILE" "$SECRETS_FILE"
"$ROOT_DIR/scripts/render/render-dashboard.sh" "$ENV_FILE"

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "${profile_args[@]}" up -d
