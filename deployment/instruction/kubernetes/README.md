# Deployment Instructions (Kubernetes)

This directory contains a minimal, portable deployment for external organizations.
The deployment is organized into one required section and three optional sections.

## Requirements

- Access to a Kubernetes cluster (kubeconfig locally).
- Ansible + `kubernetes.core` collection.
- Package with secrets in YAML format (separate, private repository).

Collection installation (if needed):

```bash
ansible-galaxy collection install kubernetes.core
```

## Quick Start

1. Copy this directory to the admin machine (or to an installation repository).
2. Fill in settings in [vars/shared_vars.yaml](vars/shared_vars.yaml).
3. Fill secret values in [vars/secrets.yaml](vars/secrets.yaml) (grouped by service).
4. Copy secret files to the `secrets/` directory (see [secrets/README.md](secrets/README.md) for examples).
5. Decide which optional sections are needed for the participant.
6. Run deployment:

```bash
ansible-playbook deploy.yaml
```

## How It Works

- `deploy.yaml` triggers subsequent playbooks.
- `deploy-secrets.yaml` loads all YAML files from `secrets/` and renders Jinja variables from `vars/shared_vars.yaml` and `vars/secrets.yaml`.
- `deploy-databases.yaml` starts the stateful section components: connector DB, optional Keycloak DB, optional Identity Hub DB, and optional Vault.
- `deploy-stateless-services.yaml` starts connector, dashboard, and optional application services.
- `deploy-routes.yaml` creates Ingress resources.

## Deployment Model

There is one required base and three optional sections.

Required base:

- connector
- connector DB
- dashboard

Optional sections:

- `identity-provider` = keycloak + keycloak DB
- `identity-hub` = identity-hub + identity-hub DB + Vault
- `storage` = storage + consumer-backend

Do not enable only one service from an optional section. The sections are grouped by responsibility, not by image count.

## Configuration in shared_vars

Most important fields in [vars/shared_vars.yaml](vars/shared_vars.yaml):

- `k8s_namespace`: namespace for services.
- `image_tag`: image tag from Docker Hub.
- `hosts` section: host addresses for Ingress.
- `connector_id`: connector instance identifier (set once per new connector deployment).
- `connector_participant_id`: connector DID/participant ID used by EDC; by default derived from `identity_hub_host` + `connector_id`, can be overridden explicitly.
- `public_scheme`: public address scheme (http or https).
- `connector_db_*`, `keycloak_db_*`, `identity_hub_db_*`: database parameters.
- `ingress_tls_enabled`, `ingress_tls_secret_name`: TLS for Ingress (optional).
- `is_auth`: enables/disables token-based auth for connector APIs (defaults to enabled).
- `connector_management_audience`: audience for management API (defaults to `connector_id`).
- `enable_identity_provider`, `enable_identity_hub`, `enable_storage`: optional deployment sections.
- `identity_hub_vault_instance`, `vault_*`: Vault settings for the `identity-hub` section.

Database service names (default):

- connector DB: <application>-connector-db
- keycloak DB: <application>-keycloak-db
- identity-hub DB: <application>-identity-hub-db

## Secrets

In the secret package, we expect YAML files with type `Secret`. e.g.:

See [secrets/README.md](secrets/README.md) for detailed examples and templates.

Required keys in database secrets:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### Secrets expected in `secrets/`:

- `connector.yaml`
- `connector-db.yaml`
- `keycloak.yaml`
- `keycloak-db.yaml`
- `identity-hub.yaml`
- `identity-hub-db.yaml`
- `storage.yaml`
- `consumer-backend.yaml`

Critical note:
Connector and Identity Hub both rely on the same Vault endpoint in this setup. If you enable `identity-hub`, you must provide valid Vault bootstrap and runtime secrets.

Operational note:
This deployment creates Vault pods and persistent storage, but it does not automate `vault operator init`, unseal, or secret seeding.

Secret values should be maintained centrally in [vars/secrets.yaml](vars/secrets.yaml) and referenced from secret manifests with `{{ secrets.<service>.<key> }}`.

Secret values should be maintained centrally in [vars/secrets.yaml](vars/secrets.yaml) and referenced from secret manifests with `{{ secrets.<service>.<key> }}`.

Critical note:
Different services must contain matching credentials as they share components or use each others. If they diverge, the section deploys but does not work.

## Verification

After deployment, you can check the status of resources:

```bash
kubectl -n <namespace> get deploy,svc,ingress
```

## Notes

- Required section is always deployed; optional sections are controlled by `enable_identity_provider`, `enable_identity_hub`, and `enable_storage`.
- Databases and storage are deployed as StatefulSets because they own persistent data; a standalone PVC is just storage allocation and not a workload controller.
- Vault is also deployed locally from templates in this directory, so this instruction no longer depends on external task files.
- Vault deployment covers Kubernetes resources only. Vault initialization, unseal, and secret bootstrap still require an explicit operational step after deployment.
- Storage and consumer-backend ingresses are created when `enable_storage=true`.
- Images come from Docker Hub: `psncedcmvds/connector`, `psncedcmvds/data-dashboard`, `psncedcmvds/identity-provider`.
- Templates in `templates/*.yaml` are rendered by Ansible (they contain Jinja `{% if %}` blocks).

## Practical Rules

- If a participant does not need login and realm management, disable `identity-provider`.
- If a participant does not need Identity Hub APIs and Vault-backed secret material, disable `identity-hub`.
- If a participant does not need internal S3-compatible storage for transfers, disable `storage`.
- Keep section ownership strict. Do not move services between sections just because two images happen to talk to each other.
