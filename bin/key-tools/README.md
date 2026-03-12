# iShare Key Tools

Helper scripts for:
- generating an iShare-compliant private key (PEM) and CSR,
- uploading the private key to Hashicorp Vault.

## Files

- `generate_pkey_csr.sh`  
  Bash script that generates:
  - `ishare-private-key.pem` (RSA-2048, PKCS#8)
  - `ishare.csr` (with `organizationIdentifier`, OID `2.5.4.97`)
  - `ishare-csr.cnf` (OpenSSL config used for the CSR)

- `upload_private_key_to_vault.py`  
  Python script that stores the private key in Hashicorp Vault KV v2 under the `content` field.

- `requirements.txt`  
  Python dependencies (`hvac`).

## Requirements

### Bash script
- `openssl` available in PATH

### Python script
- Python 3.10+
- Dependencies from `requirements.txt`

Installation:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Full workflow

### Step 1 — Generate private key and CSR

```bash
chmod +x ./generate_pkey_csr.sh
./generate_pkey_csr.sh
```

With variable overrides:

```bash
COUNTRY_CODE=PL \
ORGANIZATION_NAME="PSNC" \
COMMON_NAME="EU.EORI.PL123456789" \
ORG_IDENTIFIER="NTRPL-PSNC" \
DNS_NAME="connector.psnc.pl" \
OUT_DIR="./out" \
./generate_pkey_csr.sh
```

This produces `ishare-private-key.pem` and `ishare.csr` in the output directory.

### Step 2 — Submit CSR to the iShare CA

Use the generated `ishare.csr` to request a certificate from the iShare CA.

- Guide: [iSHARE eSEALs CSR Guide](https://github.com/iSHAREScheme/eSEALsGuide/blob/main/CSR.md)
- iShare test CA enrollment: [https://ca7.isharetest.net:8442/ejbca/ra/enrollmakenewrequest.xhtml](https://ca7.isharetest.net:8442/ejbca/ra/enrollmakenewrequest.xhtml)

The CA will issue a certificate chain (`.pem`) once the request is approved.

### Step 3 — Upload private key to Hashicorp Vault

Option A: via environment variables (`VAULT_ADDR`, `VAULT_TOKEN`)

```bash
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="<token>"
python upload_private_key_to_vault.py \
  --private-key-file ./out/ishare-private-key.pem \
  --mount-point secret \
  --secret-path ishare-private-key
```

Option B: explicit CLI parameters

```bash
python upload_private_key_to_vault.py \
  --vault-url "http://localhost:8200" \
  --vault-token "<token>" \
  --private-key-file ./out/ishare-private-key.pem \
  --mount-point secret \
  --secret-path ishare-private-key
```

### Step 4 — Register in the Participant Registry

Register the connector as a participant in the iShare Participant Registry (PR), providing the certificate chain `.pem` issued by the CA. A PR administrator must review and approve the registration request.

Once approved, set the following in the connector configuration:

```properties
ishare.vault.key.secret=ishare-private-key
ishare.vault.cert.secret=<vault-secret-name-for-cert-chain>
```

To store the certificate chain in Vault as well:

```bash
vault kv put secret/ishare-certificate-chain content=@ishare-cert-chain.pem
```
