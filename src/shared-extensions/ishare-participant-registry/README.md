# iShare Participant Registry Extension

EDC extension for integration with the iShare Participant Registry (PR).

It provides:
- OAuth2 M2M token management with cache and validity checks
- Access to PR endpoints: `/parties`, `/trusted_list`, `/dataspaces`, `/frameworks`
- REST API for integration testing and operational use
- JWT client assertion signing with certificate chain (`x5c` header), aligned with iShare requirements

## Documentation

| Document | Purpose |
|----------|---------|
| [OPENAPI_USAGE.md](OPENAPI_USAGE.md) | OpenAPI import (Postman/Insomnia), API client generation |
| [key-tools/README.md](../../../bin/key-tools/README.md) | Key/CSR generation and Vault upload scripts |

## Dependencies

- EDC v0.14.0
- Nimbus JOSE JWT 9.37.3
- OkHttp 4.12.0
- Jackson 2.15.3
- Swagger Annotations 2.2.20 (OpenAPI 3.0)

## Certificate and Registration Flow (Extension Context)

This extension assumes the key and certificate are prepared outside of the connector runtime.

1. Generate private key and CSR using scripts from `bin/key-tools`.
2. Submit CSR to an iShare-compatible CA.
3. Register participant in PR with the issued certificate chain (`.pem`) and wait for PR admin approval.
4. Store private key and certificate chain in Hashicorp Vault.
5. Configure this extension with Vault secret names.

Important:
- iShare PR requires CA-signed certificates. Self-signed certificates are rejected.
- CSR `organizationIdentifier` (OID `2.5.4.97`) must follow: `NTR<2-letter-country-code>-<Organization-name>`.
- `ishare.pr.id` must be the official DID/EORI of the PR operator (used as `aud`), not inferred from URL.

Reference links:
- iSHARE eSEALs CSR Guide: https://github.com/iSHAREScheme/eSEALsGuide/blob/main/CSR.md
- iShare test CA enrollment: https://ca7.isharetest.net:8442/ejbca/ra/enrollmakenewrequest.xhtml

## Configuration

Private key and certificate chain are stored in Hashicorp Vault (using the same Vault instance already configured for EDC via `edc.vault.hashicorp.*`). 

```properties
# iShare Participant Registry
ishare.pr.url=https://pr.example.com

# Organization identifier used as iss and sub in JWT client assertions
ishare.client.id=EU.EORI.NL000000000

# DID or EORI of the Participant Registry (used as aud in JWT)
ishare.pr.id=EU.EORI.NLAUTHORITYID

# Vault secret names (stored as: vault kv put secret/<name> content=@file.pem)
ishare.vault.key.secret=ishare-private-key
ishare.vault.cert.secret=ishare-certificate-chain

ishare.auto.init=true
```

Claim mapping used by the extension:
- `iss` = `ishare.client.id`
- `sub` = `ishare.client.id`
- `aud` = `ishare.pr.id`

## REST API

After starting the stack with docker compose, the API is exposed on the host using these ports:

```text
Consumer connector:   http://localhost:8080/api/ishare/*
Provider connector:   http://localhost:8190/api/ishare/*
Federated catalog:    http://localhost:8290/api/ishare/*
```

The examples below use the consumer connector.

Main endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ishare/token` | GET | Get token (or refresh if expired) |
| `/api/ishare/token/status` | GET | Check token status |
| `/api/ishare/parties` | GET | List participants |
| `/api/ishare/parties/{partyId}` | GET | Get participant details |
| `/api/ishare/trusted_list` | GET | Get trusted certificates |
| `/api/ishare/dataspaces` | GET | List dataspaces |
| `/api/ishare/dataspaces/{dataspaceId}` | GET | Get dataspace details |
| `/api/ishare/frameworks` | GET | List frameworks |
| `/api/ishare/frameworks/{frameworkId}` | GET | Get framework details |

OpenAPI:
- Full specification: [openapi.yaml](openapi.yaml)
- Usage guide: [OPENAPI_USAGE.md](OPENAPI_USAGE.md)
- EDC runtime endpoint (if enabled on consumer connector): `http://localhost:8080/api/openapi`

## Build and Test

1. Build shared extensions:

```bash
cd src/shared-extensions
./gradlew clean build publishToMavenLocal
```

2. Build connector or federated catalog:

```bash
cd src/edc-connector
./gradlew clean build

# or

cd src/federated-catalog
./gradlew clean build
```

3. Run with config:

```bash
java -Dedc.fs.config=config.properties -jar launchers/dcp/build/libs/connector.jar
```

4. Quick API checks:

```bash
curl -X GET http://localhost:8080/api/ishare/token/status
curl -X GET http://localhost:8080/api/ishare/token
curl -X GET http://localhost:8080/api/ishare/parties
```

## Setup and Testing (End-to-End)

### Architecture Flow

```text
EDC Connector (CT/FC)
   -> IShareParticipantRegistryExtension
       -> IShareTokenService (loads key+cert from Vault, creates JWT with x5c, caches token)
       -> IShareParticipantRegistryClient (calls PR endpoints)
       -> IShareParticipantRegistryApiExtension (exposes /api/ishare/*)
   -> POST /connect/token to PR with signed JWT client assertion

iShare Participant Registry (PR)
   -> validates x5c and JWT claims
   -> returns access_token
```

### Pre-Setup Checklist

- Key pair and CSR generated via `bin/key-tools`
- CSR submitted to CA and CA-signed certificate chain received
- Participant registered in PR (admin approval completed)
- Private key and certificate chain stored in Hashicorp Vault
- Connector/federated-catalog configuration updated with iShare properties

### Store Secrets in Vault

```bash
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=<vault-token>

vault kv put secret/ishare-private-key content=@ishare-private-key.pem
vault kv put secret/ishare-certificate-chain content=@ishare-cert-chain.pem

vault kv get -field=content secret/ishare-private-key | head -3
vault kv get -field=content secret/ishare-certificate-chain | head -3
```

If you run multiple runtime profiles (provider/consumer/federated-catalog), store both secrets in each Vault instance used by those runtimes.

### Docker Runtime

Option A (recommended):

```bash
cd /Users/matt/dev/psnc-edc-mvds/docker
make build
make up
make logs container=edc-connector
```

Option B (direct compose):

```bash
cd /Users/matt/dev/psnc-edc-mvds/docker
docker-compose -f compose/base.yaml -f compose/consumer.yaml -f compose/local.yaml up -d
docker ps
docker logs edc-connector
docker logs federated-catalog
```

### Verify Extension Initialization

```bash
docker logs edc-connector | grep -i "ishare"
```

Expected messages include successful initialization of:
- `IShareParticipantRegistryExtension`
- `IShareParticipantRegistryApiExtension`

### API Verification

Token flow:

```bash
curl -X GET http://localhost:8080/api/ishare/token
curl -X GET http://localhost:8080/api/ishare/token/status
curl -X GET "http://localhost:8080/api/ishare/token?refresh=true"
```

Resource endpoints:

```bash
curl -X GET http://localhost:8080/api/ishare/parties
curl -X GET http://localhost:8080/api/ishare/trusted_list
curl -X GET http://localhost:8080/api/ishare/dataspaces
curl -X GET http://localhost:8080/api/ishare/frameworks
```

### Troubleshooting

- `401` or `403` from token endpoint:
   - verify `ishare.client.id` matches PR registration
   - verify `ishare.pr.id` is the official PR DID/EORI
   - verify participant registration is approved in PR
   - verify Vault secrets exist and contain valid PEM values

- Token fetch hangs or times out:
   - verify `ishare.pr.url` reachability from container
   - check connector logs for network and SSL errors

- Signature verification errors:
   - private key and certificate chain do not match
   - certificate chain order is incorrect (end-entity first)

Useful log commands:

```bash
docker logs -f edc-connector | grep -i "ishare\|token\|jwt"
docker logs edc-connector | grep -i "error\|exception" | grep -i "ishare"
```

### Production Checklist

- CA-signed certificate chain in use (not self-signed)
- Private key stored only in Vault and excluded from Git
- `ishare.auto.init` set according to environment policy
- Monitoring for token acquisition failures enabled
- Certificate rotation process documented and tested

## Architecture

Core components:

1. `IShareTokenService`
   - Manages OAuth2 M2M tokens
   - Caches tokens with 60-second safety buffer
   - Creates iShare-compliant JWT client assertions

2. `IShareParticipantRegistryClient`
   - Calls PR API endpoints
   - Reuses current valid token automatically
   - Parses JSON responses

3. `IShareParticipantRegistryExtension`
   - Initializes services
   - Validates configuration
   - Registers providers for other extensions

4. `IShareParticipantRegistryApiExtension`
   - Registers REST controller
   - Integrates with EDC WebService

## Security Notes

- Private key is stored in Hashicorp Vault (PKCS#8 PEM secret).
- JWT client assertion is generated on demand (30-second validity).
- Access token is cached in memory only.
- Keep sensitive configuration in secure secret management.

## References

- [iShare M2M Access Token](https://dev.ishare.eu/all-roles-common-endpoints/access-token-m2m)
- [iShare Participant Registry](https://dev.ishare.eu/participant-registry-role/getting-started)
- [iShare Parties API](https://dev.ishare.eu/participant-registry-role/parties)
- [iShare Trusted List](https://dev.ishare.eu/participant-registry-role/trusted-list)
- [iShare Dataspaces](https://dev.ishare.eu/participant-registry-role/dataspaces)
- [iShare Frameworks](https://dev.ishare.eu/participant-registry-role/frameworks)
