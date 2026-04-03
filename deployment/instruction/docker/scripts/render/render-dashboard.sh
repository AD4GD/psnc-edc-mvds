#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="$ROOT_DIR/.generated/config/dashboard"
CONFIG_FILE="$OUT_DIR/app.config.json"
NGINX_CONF_TARGET="$OUT_DIR/nginx.conf"
ENV_FILE="${1:-$ROOT_DIR/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"

mkdir -p "$OUT_DIR"

PUBLIC_SCHEME="${PUBLIC_SCHEME:-http}"
CONNECTOR_HOST="${CONNECTOR_HOST:-connector.test}"
KEYCLOAK_HOST="${KEYCLOAK_HOST:-keycloak.test}"
CONNECTOR_MANAGEMENT_PATH="${CONNECTOR_MANAGEMENT_PATH:-/api/management}"
CONNECTOR_CATALOG_PATH="${CONNECTOR_CATALOG_PATH:-/api/catalog-proxy/catalog/request}"
CONSUMER_BACKEND_URL="http://consumer-backend:4000/edr-endpoint"
OAUTH_CLIENT_ID="${OAUTH_CLIENT_ID:-data-space-users}"
CONNECTOR_ID="${CONNECTOR_ID:-connector}"

# Render app.config.json
echo "Rendering dashboard config..." >&2
cat > "$CONFIG_FILE" << EOF
{
  "managementApiUrl": "${PUBLIC_SCHEME}://${CONNECTOR_HOST}${CONNECTOR_MANAGEMENT_PATH}",
  "catalogUrl": "${PUBLIC_SCHEME}://${CONNECTOR_HOST}${CONNECTOR_CATALOG_PATH}",
  "theme": "theme-3",
  "deploymentMode": "production",
  "backendUrl": "${CONSUMER_BACKEND_URL}",
  "oauthIssuer": "${PUBLIC_SCHEME}://${KEYCLOAK_HOST}/realms/Organizations",
  "oauthClientId": "${OAUTH_CLIENT_ID}",
  "connectorId": "${CONNECTOR_ID}"
}
EOF

# Render nginx.conf
echo "Rendering nginx config..." >&2
cat > "$NGINX_CONF_TARGET" << EOF
events {}
pid /tmp/nginx.pid;
http {
  include /etc/nginx/mime.types;
  server {
    listen       80;
    server_name  localhost;

    root   /usr/share/nginx/html;
    index  index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /management {
    proxy_pass http://connector:8081${CONNECTOR_MANAGEMENT_PATH};
    }

    location /catalog-proxy/ {
    proxy_pass http://connector:8086${CONNECTOR_CATALOG_PATH};
    }

    location /catalog {
    proxy_pass http://connector:8086${CONNECTOR_CATALOG_PATH};
    }
  }
}
EOF
echo "Rendered dashboard config to: $OUT_DIR" >&2