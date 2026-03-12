#!/usr/bin/env bash
set -euo pipefail

# Generates:
# - RSA private key in PKCS#8 PEM
# - CSR based on iShare eSEALs profile (organizationIdentifier OID 2.5.4.97)

OUT_DIR="${OUT_DIR:-.}"
COUNTRY_CODE="${COUNTRY_CODE:-PL}"
ORGANIZATION_NAME="${ORGANIZATION_NAME:-PCSS Provider 1}"
COMMON_NAME="${COMMON_NAME:-PCSS Provider 1}"
ORG_IDENTIFIER="${ORG_IDENTIFIER:-NTR${COUNTRY_CODE}-PCSSPROVIDER1}"
PRIVATE_KEY_FILE="${PRIVATE_KEY_FILE:-${OUT_DIR}/ishare-private-key.pem}"
CSR_FILE="${CSR_FILE:-${OUT_DIR}/ishare.csr}"
CSR_CONFIG_FILE="${CSR_CONFIG_FILE:-${OUT_DIR}/ishare-csr.cnf}"
ENCRYPT_PRIVATE_KEY="${ENCRYPT_PRIVATE_KEY:-false}"

mkdir -p "${OUT_DIR}"

cat > "${CSR_CONFIG_FILE}" <<EOF
[ req ]
default_bits       = 2048
prompt             = no
distinguished_name = dn
req_extensions     = v3_req
oid_section        = custom_oids

[ custom_oids ]
organizationIdentifier = 2.5.4.97

[ dn ]
C  = ${COUNTRY_CODE}
O  = ${ORGANIZATION_NAME}
CN = ${COMMON_NAME}
organizationIdentifier = ${ORG_IDENTIFIER}

[ v3_req ]
keyUsage = critical, digitalSignature, nonRepudiation
EOF

if [[ "${ENCRYPT_PRIVATE_KEY}" == "true" ]]; then
  echo "Generating encrypted RSA private key (PKCS#8 PEM)..."
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -aes256 -out "${PRIVATE_KEY_FILE}"
else
  echo "Generating RSA private key (PKCS#8 PEM)..."
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "${PRIVATE_KEY_FILE}"
fi

echo "Generating CSR using ${CSR_CONFIG_FILE}..."
openssl req -new \
  -key "${PRIVATE_KEY_FILE}" \
  -config "${CSR_CONFIG_FILE}" \
  -out "${CSR_FILE}"

echo
echo "Generated files:"
echo "  Private key: ${PRIVATE_KEY_FILE}"
echo "  CSR:         ${CSR_FILE}"
echo "  Config:      ${CSR_CONFIG_FILE}"
echo
echo "Verification (Subject with organizationIdentifier):"
openssl req -in "${CSR_FILE}" -noout -subject -nameopt RFC2253
echo
openssl req -in "${CSR_FILE}" -noout -text | grep -A2 "Subject:" || true
