# Secrets Directory

This directory contains Kubernetes Secret definitions required for deployment.

## Templates
Keep secret manifests as templates with `{{ ... }}` variables and set actual values centrally in `../vars/secrets.yaml`.
`deploy-secrets.yaml` renders these templates during apply.

## Required Secrets

### connector-db.yaml
PostgreSQL credentials for the connector database.

**Required keys:**
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### keycloak-db.yaml
PostgreSQL credentials for the Keycloak database.

**Required keys:**
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### connector.yaml
EDC Connector configuration including database connection, OAuth, and API keys.

**Key environment variables:**
- `EDC_DATASOURCE_DEFAULT_URL` - JDBC connection string to connector DB
- `EDC_DATASOURCE_DEFAULT_USER` - Database username
- `EDC_DATASOURCE_DEFAULT_PASSWORD` - Database password
- `EDC_API_AUTH_KEY` - API authentication key
- OAuth/OIDC configuration (if using Keycloak integration)

### keycloak.yaml
Keycloak configuration including admin credentials and database connection.

**Key environment variables:**
- `KEYCLOAK_ADMIN` - Admin username
- `KEYCLOAK_ADMIN_PASSWORD` - Admin password
- `KC_DB_URL` - JDBC connection string to keycloak DB
- `KC_DB_USERNAME` - Database username
- `KC_DB_PASSWORD` - Database password

### identity-hub.yaml (Optional)
Identity Hub runtime secrets.

**Key environment variables:**
- `EDC_VAULT_HASHICORP_TOKEN`
- `EDC_IH_API_SUPERUSER_KEY`

### identity-hub-db.yaml (Optional)
PostgreSQL credentials for the Identity Hub database.

**Required keys:**
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `EDC_DATASOURCE_DEFAULT_USER`
- `EDC_DATASOURCE_DEFAULT_PASSWORD`

### storage.yaml (Optional — if storage enabled)
RustFS S3-compatible storage access credentials.

**Required keys:**
- `RUSTFS_ACCESS_KEY` - access key for S3 API
- `RUSTFS_SECRET_KEY` - secret key for S3 API

### consumer-backend.yaml (Optional — if consumer backend enabled)
Credentials for consumer-backend to authenticate against the internal S3 storage.

**Required keys:**
- `S3_ACCESS_KEY` - S3 access key (must match `RUSTFS_ACCESS_KEY` in storage.yaml)
- `S3_SECRET_KEY` - S3 secret key (must match `RUSTFS_SECRET_KEY` in storage.yaml)

## Security Notes

⚠️ **NEVER commit actual secrets to version control!**

- Keep this directory in `.gitignore` (except `.example` files)
- Store actual secrets in a secure location (e.g., HashiCorp Vault, sealed-secrets)
- Rotate credentials regularly
- Use strong, unique passwords for each service
