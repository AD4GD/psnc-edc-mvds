#!/bin/bash

#
# Dataspace Verification Script
#
# Verifies that a dataspace initialized by init-dataspace is healthy:
#   - Checks that Verifiable Credentials are stored in each Identity Hub
#   - Checks that the DID document is published with valid (non-localhost) service endpoints
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
# Verify Data Space Hub reachability via /.well-known/did.json
# ---------------------------------------------------------------------------

verify_data_space_hub() {
    local dsh_url
    dsh_url=$(jq -r '.data_space_hub.url' "$CONFIG_DIR/dataspace.json")

    if [ -z "$dsh_url" ] || [ "$dsh_url" = "null" ]; then
        warn "data_space_hub.url not set in dataspace.json — skipping DID document check"
        return
    fi

    log "--- Verifying Data Space Hub ---"
    log "Checking /.well-known/did.json at ${dsh_url}..."

    local did_url="${dsh_url%/}/.well-known/did.json"
    local did_response did_status did_body

    did_response=$(curl -sk -w "\n%{http_code}" \
        --max-time 10 \
        "${did_url}" 2>/dev/null) || true
    did_status=$(echo "$did_response" | tail -1)
    did_body=$(echo "$did_response" | sed '$d')

    if [ "$did_status" = "200" ]; then
        local did_id
        did_id=$(echo "$did_body" | jq -r '.id // empty' 2>/dev/null || echo "")
        if [ -n "$did_id" ]; then
            ok "Data Space Hub: DID document reachable (id: ${did_id})"
        else
            warn "Data Space Hub: /.well-known/did.json returned 200 but no 'id' field found"
        fi
        if [ "$VERBOSE" = true ]; then
            echo "$did_body" | jq '.' 2>/dev/null || echo "$did_body"
        fi
    elif [ "$did_status" = "000" ]; then
        fail_check "Data Space Hub: UNREACHABLE at ${dsh_url} — DID documents cannot be resolved, DCP auth will fail for all participants"
    else
        fail_check "Data Space Hub: /.well-known/did.json returned HTTP ${did_status} (expected 200)"
        if [ "$VERBOSE" = true ]; then
            echo "$did_body"
        fi
    fi

    echo ""
}

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

    # For this DSH request only: when using HTTP, force localhost as the host.
    local ih_identity_url_for_request="$ih_identity_url"
    if [[ "$ih_identity_url_for_request" =~ ^http://[^/:]+(:[0-9]+)?(.*)$ ]]; then
        ih_identity_url_for_request="http://localhost${BASH_REMATCH[1]}${BASH_REMATCH[2]}"
    fi

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
        "${ih_identity_url_for_request}/v1alpha/participants/${did}/credentials" \
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

    # ----- Check 2: DID document published and service endpoints valid -----

    log "Checking DID document for ${name} in Identity Hub..."

    local participant_b64
    participant_b64=$(echo -n "${did}" | base64 -w0)
    local did_b64
    did_b64=$(echo -n "${did}" | base64 -w0 | tr '+/' '-_' | tr -d '=')

    local did_response did_status did_body
    did_response=$(curl -sk -w "\n%{http_code}" \
        --max-time 10 \
        "${ih_identity_url_for_request}/v1alpha/participants/${participant_b64}/dids/query" \
        -H "x-api-key: ${ih_api_key}" \
        -H "Content-Type: application/json" \
        -d '{}' 2>/dev/null) || true
    did_status=$(echo "$did_response" | tail -1)
    did_body=$(echo "$did_response" | sed '$d')

    if [ "$did_status" = "000" ]; then
        fail_check "${name}: Identity Hub identity API unreachable at ${ih_identity_url}"
    elif [ "$did_status" != "200" ]; then
        fail_check "${name}: DID document query failed (HTTP ${did_status})"
    else
        # Find the DID document matching the participant's DID (skip super-user etc.)
        local participant_did_doc
        participant_did_doc=$(echo "$did_body" | jq -r --arg did "$did" '.[] | select(.id == $did)' 2>/dev/null || echo "")

        if [ -z "$participant_did_doc" ]; then
            fail_check "${name}: DID document for '${did}' not found in Identity Hub"
        else
            ok "${name}: DID document found in Identity Hub"

            if [ "$VERBOSE" = true ]; then
                echo "$participant_did_doc" | jq '.' 2>/dev/null || echo "$participant_did_doc"
            fi

            # Check all service endpoints do NOT use localhost
            local bad_endpoints
            bad_endpoints=$(echo "$participant_did_doc" | jq -r '
                .service[]? | select(.serviceEndpoint | test("localhost|127\\.0\\.0\\.1")) |
                "  • \(.id): \(.serviceEndpoint)"' 2>/dev/null || echo "")

            if [ -n "$bad_endpoints" ]; then
                fail_check "${name}: DID document contains service endpoint(s) with 'localhost' — other containers cannot resolve them:"
                echo "$bad_endpoints" >&2
            else
                ok "${name}: All DID service endpoints use resolvable hostnames"
            fi

            # Check there is at least a CredentialService and a ProtocolEndpoint
            local cred_svc
            cred_svc=$(echo "$participant_did_doc" | jq -r '.service[]? | select(.type == "CredentialService") | .serviceEndpoint' 2>/dev/null || echo "")
            local dsp_svc
            dsp_svc=$(echo "$participant_did_doc" | jq -r '.service[]? | select(.type == "ProtocolEndpoint") | .serviceEndpoint' 2>/dev/null || echo "")

            if [ -z "$cred_svc" ]; then
                fail_check "${name}: DID document is missing a 'CredentialService' endpoint"
            else
                log "  CredentialService: ${cred_svc}"
            fi

            if [ -z "$dsp_svc" ]; then
                warn "${name}: DID document has no 'ProtocolEndpoint' (DSP) — may be intentional for this participant"
            else
                log "  ProtocolEndpoint:  ${dsp_svc}"
            fi
        fi
    fi

    # ----- Check 3: STS client secret in connector vault -----

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

    verify_data_space_hub

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
