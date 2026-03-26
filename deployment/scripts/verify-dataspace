#!/bin/bash

#
# Dataspace Verification Script
#
# Verifies that a dataspace initialized by init-dataspace is healthy:
#   - Checks that Verifiable Credentials are stored in each Identity Hub
#   - Checks that STS client secrets are stored in each connector's vault
#
# Uses the same config directory as init-dataspace.
#
# Usage:
#   ./verify-dataspace --config <config-dir>
#   ./verify-dataspace --config <config-dir> --participant consumer
#   e.g. ./verify-dataspace --config config/sage-init-dataspace
# Config directory must contain:
#   dataspace.json      - global settings
#   participants/*.json - one file per participant
#

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

CONFIG_DIR=""
SINGLE_PARTICIPANT=""
VERBOSE=false
EXIT_CODE=0

usage() {
    echo "Usage: $0 --config <config-dir> [--participant <name>] [--verbose]"
    echo ""
    echo "Options:"
    echo "  --config <dir>          Path to config directory (required, same as init-dataspace)"
    echo "  --participant <name>    Only verify a single participant (matches filename without .json)"
    echo "  --verbose               Show full API responses"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_DIR="$2"; shift 2 ;;
        --participant)
            SINGLE_PARTICIPANT="$2"; shift 2 ;;
        --verbose)
            VERBOSE=true; shift ;;
        -h|--help)
            usage ;;
        *)
            echo "Unknown option: $1"; usage ;;
    esac
done

if [ -z "$CONFIG_DIR" ]; then
    echo "Error: --config is required"
    usage
fi

if [ ! -f "$CONFIG_DIR/dataspace.json" ]; then
    echo "Error: $CONFIG_DIR/dataspace.json not found"
    exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { echo "[verify-dataspace] $(date +%H:%M:%S) $*"; }
ok()   { echo "[verify-dataspace] $(date +%H:%M:%S) ✅ $*"; }
warn() { echo "[verify-dataspace] $(date +%H:%M:%S) ⚠️  $*"; }
fail_check() { echo "[verify-dataspace] $(date +%H:%M:%S) ❌ $*"; EXIT_CODE=1; }

# ---------------------------------------------------------------------------
# Verify a single participant
# ---------------------------------------------------------------------------

verify_participant() {
    local config_file="$1"
    local name
    name=$(basename "$config_file" .json)

    log "--- Verifying participant: ${name} ---"

    # Read participant config
    local did ih_identity_url ih_api_key
    local connector_mgmt_url connector_api_key

    did=$(jq -r '.did' "$config_file")
    ih_identity_url=$(jq -r '.identity_hub.identity_api_url' "$config_file")
    ih_api_key=$(jq -r '.identity_hub.api_key' "$config_file")
    connector_mgmt_url=$(jq -r '.connector.management_api_url' "$config_file")
    connector_api_key=$(jq -r '.connector.api_key' "$config_file")

    # Read optional short secret alias (must match init-dataspace and Ansible vars)
    local sts_client_secret_alias
    sts_client_secret_alias=$(jq -r '.sts_client_secret_alias // empty' "$config_file")
    if [ -z "$sts_client_secret_alias" ]; then
        sts_client_secret_alias="${did}-sts-client-secret"
    fi

    # ----- Check 1: Verifiable Credentials in Identity Hub -----

    log "Checking VCs for ${name} in Identity Hub..."

    local vc_response vc_status vc_body
    vc_response=$(curl -sk -w "\n%{http_code}" \
        --max-time 10 \
        "${ih_identity_url}/v1alpha/participants/${did}/credentials" \
        -H "x-api-key: ${ih_api_key}" 2>/dev/null) || true
    vc_status=$(echo "$vc_response" | tail -1)
    vc_body=$(echo "$vc_response" | sed '$d')

    if [ "$vc_status" = "200" ]; then
        local vc_count
        vc_count=$(echo "$vc_body" | jq 'if type == "array" then length else 0 end' 2>/dev/null || echo "0")

        if [ "$vc_count" -gt 0 ]; then
            ok "${name}: Found ${vc_count} credential(s) in Identity Hub"

            # List credential types
            local vc_types
            vc_types=$(echo "$vc_body" | jq -r '
                if type == "array" then
                    [.[] | .verifiableCredential.credential.type // .credentialStatus // "unknown"] | flatten | unique | join(", ")
                else
                    "unknown"
                end' 2>/dev/null || echo "unknown")
            log "  Credential types: ${vc_types}"

            if [ "$VERBOSE" = true ]; then
                echo "$vc_body" | jq '.' 2>/dev/null || echo "$vc_body"
            fi
        else
            fail_check "${name}: No credentials found in Identity Hub (empty response)"
        fi
    elif [ "$vc_status" = "000" ]; then
        fail_check "${name}: Identity Hub identity API unreachable at ${ih_identity_url}"
    else
        fail_check "${name}: Identity Hub credentials query failed (HTTP ${vc_status})"
        if [ "$VERBOSE" = true ]; then
            echo "$vc_body"
        fi
    fi

    # ----- Check 2: STS client secret in connector vault -----

    log "Checking STS client secret for ${name} in connector..."

    local secret_id="${sts_client_secret_alias}"
    local secret_response secret_status secret_body
    secret_response=$(curl -sk -w "\n%{http_code}" \
        --max-time 10 \
        "${connector_mgmt_url}/v3/secrets/${secret_id}" \
        -H "x-api-key: ${connector_api_key}" 2>/dev/null) || true
    secret_status=$(echo "$secret_response" | tail -1)
    secret_body=$(echo "$secret_response" | sed '$d')

    if [ "$secret_status" = "200" ]; then
        ok "${name}: STS client secret exists in connector vault"
        if [ "$VERBOSE" = true ]; then
            echo "$secret_body" | jq '.' 2>/dev/null || echo "$secret_body"
        fi
    elif [ "$secret_status" = "404" ]; then
        fail_check "${name}: STS client secret NOT found in connector vault (secret ID: ${secret_id})"
    elif [ "$secret_status" = "000" ]; then
        fail_check "${name}: Connector management API unreachable at ${connector_mgmt_url}"
    else
        warn "${name}: Unexpected response checking secret (HTTP ${secret_status})"
        if [ "$VERBOSE" = true ]; then
            echo "$secret_body"
        fi
    fi

    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    log "=========================================="
    log "  Dataspace Verification"
    log "  Config: ${CONFIG_DIR}"
    if [ -n "$SINGLE_PARTICIPANT" ]; then
        log "  Participant: ${SINGLE_PARTICIPANT}"
    fi
    log "=========================================="
    echo ""

    if [ -n "$SINGLE_PARTICIPANT" ]; then
        local config_file="$CONFIG_DIR/participants/${SINGLE_PARTICIPANT}.json"
        if [ ! -f "$config_file" ]; then
            echo "Error: Participant config not found: $config_file"
            exit 1
        fi
        verify_participant "$config_file"
    else
        for config_file in "$CONFIG_DIR"/participants/*.json; do
            [ -f "$config_file" ] || continue
            verify_participant "$config_file"
        done
    fi

    log "=========================================="
    if [ "$EXIT_CODE" -eq 0 ]; then
        log "  ✅ All checks passed!"
    else
        log "  ❌ Some checks failed — review output above"
    fi
    log "=========================================="

    exit "$EXIT_CODE"
}

main "$@"
