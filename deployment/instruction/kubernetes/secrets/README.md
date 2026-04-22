# Secrets Directory

This directory contains Kubernetes Secret definitions required for deployment.

## Templates
Keep secret manifests as templates with `{{ ... }}` variables and set actual values centrally in `../vars/secrets.yaml`.
`deploy-secrets.yaml` renders these templates during apply.

## Commands

### Normal secrets
Use this random generator for all password-like values:

```bash
openssl rand -base64 32 | tr -d '\n'; echo
```

### Identity-Hub super-user secret

```bash
IH_USER="super-user";  IH_SECRET="$(openssl rand -base64 24 | tr -d '\r\n')"; printf '%s.%s\n' \
  "$(printf '%s' "$IH_USER" | openssl base64 -A)" \
  "$(printf '%s' "$IH_SECRET" | openssl base64 -A)"
```

## Required Secrets

### connector-db
PostgreSQL credentials for the connector database.

**Required keys:**
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### connector
EDC Connector configuration including database connection, OAuth, and API keys.

**Key environment variables:**
- `EDC_DATASOURCE_DEFAULT_URL` - JDBC connection string to connector DB
- `EDC_DATASOURCE_DEFAULT_USER` - Database username
- `EDC_DATASOURCE_DEFAULT_PASSWORD` - Database password
- `API_AUTH_KEY` - API token-based authentication key
- `WEB_HTTP_AUTH_KEY` - API token-based authentication key
- `WEB_HTTP_MANAGEMENT_AUTH_KEY` - API token-based authentication key
- `WEB_HTTP_CONTROL_AUTH_KEY` - API token-based authentication key
- `WEB_HTTP_CATALOGPROXY_AUTH_KEY` - API token-based authentication key

- OAuth/OIDC configuration (if using Keycloak integration)

### keycloak-db
PostgreSQL credentials for the Keycloak database.

**Required keys:**
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### keycloak (Optional)
Keycloak configuration including admin credentials and database connection.

**Key environment variables:**
- `KEYCLOAK_ADMIN` - Admin username
- `KEYCLOAK_ADMIN_PASSWORD` - Admin password
- `KC_DB_URL` - JDBC connection string to keycloak DB
- `KC_DB_USERNAME` - Database username
- `KC_DB_PASSWORD` - Database password

- `ADMIN` - "admin"
- `ADMIN_PASSWORD` - "change-me-keycloak-admin-password"
- `DB` - "postgres"
- `DB_SCHEMA` - "public"
- `DB_URL` - "{{ keycloak_db_service }}"
- `DB_USERNAME` - "keycloak"
- `DB_PASSWORD` - "change-me-keycloak-db-password"

### identity-hub-db.yaml (Optional)
PostgreSQL credentials for the Identity Hub database.

**Required keys:**
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `EDC_DATASOURCE_DEFAULT_USER`
- `EDC_DATASOURCE_DEFAULT_PASSWORD`

### identity-hub (Optional)
Identity Hub runtime secrets.

**Key environment variables:**
- `IH_API_SUPERUSER_KEY` - created with a command
- `DATASOURCE_DEFAULT_USER`
- `DATASOURCE_DEFAULT_PASSWORD`

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

- Store actual secrets in a secure location
- Rotate credentials regularly
- Use strong, unique passwords for each service
