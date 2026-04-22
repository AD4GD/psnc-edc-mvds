# Deployment Instructions (Kubernetes)

## Requirements

- Access to an Openshift x Kubernetes cluster (kubeconfig locally).
- Plain Kubernetes (without OpenShift Routes) is not supported by this version yet. Plain Kubernetes support will be added later.
- Ansible + `kubernetes.core` collection.
- Package with secrets in YAML format (separate, private repository).


### Platform and tools

- OpenShift cluster access and a working kubeconfig.
- Permissions to create namespace/project resources.
- `Ansible` and `kubernetes.core` collection.
- `make`, `openssl`, `python3` (for optional bootstrap scripts).

Install collection if needed:

```bash
ansible-galaxy collection install kubernetes.core
```

### Minimum resources

Recommended minimum for a full profile (required base + optional sections):

- CPU: 4 vCPU (recommended 8 vCPU)
- RAM: 12 GiB (recommended 16 GiB)
- Storage: at least 40 GiB persistent volume space across databases, Vault, and storage service

At deployment level, resources are controlled in `vars/shared_vars.yaml` by:

- `connector_resources`, `dashboard_resources`, `keycloak_resources`, `identity_hub_resources`, `storage_resources`, `consumer_backend_resources`, `vault_resources`
- `connector_db_storage_size`, `keycloak_db_storage_size`, `identity_hub_db_storage_size`, `vault_pvc_storage_size`, `storage_pvc_size`

Collection installation (if needed):

```bash
ansible-galaxy collection install kubernetes.core
```


## Prepare namespace and Docker pull secret

### Namespace

Set your target namespace:

```bash
export NS=<your-namespace>
```

Create namespace/project if needed:

```bash
kubectl get ns "$NS" >/dev/null 2>&1 || kubectl create ns "$NS"
```

### DockerHUB secret

To prevent `ImagePullError` you need to create ImagePullSecret and connect it to the deployment phase.
1. Sign in or sign up into Docker Hub
2. Account Settings
3. Personal access tokens
4. Generate new token & copy it
5. Go to CLI and type:
```bash
kubectl create secret docker-registry dockerhub-creds --docker-server=https://index.docker.io/v1/ --docker-username=<dockerhub-user> --docker-password=<dockerhub-token> --docker-email=<email>`
```
6. Then type
```bash
oc secrets link default dockerhub-creds --for=pull
```


If the secret already exists, replace command with:

```bash
kubectl delete secret dockerhub-creds
```

and then paste previous command to create secret

OpenShift equivalent command can use `oc` instead of `kubectl`.

Verify secret:

```bash
kubectl get secret dockerhub-creds
```

## Typical flow
1. `make init` - initializes the repository for `env` files
2. Fill in settings in [vars/shared_vars.yaml](vars/shared_vars.yaml).
3. Decide which optional sections are needed for the participant.
4. Fill secret values in [vars/secrets.yaml](vars/secrets.yaml) (grouped by service).
5. `make deploy-env` - renderes `.env` files from `vars/` catalog to allow automatic scripts run later
6. `make deploy-vault` - step to create vault for the first time. You can skip 6 and 7 if vault is already up & running 
7. `make init-vault` - initializes vault, creates tokens and saves it to local secret file
8. `make sync-vault` - synchronizes vault tokens with the repository variables
8. `make deploy` - creates all of the containers \
... Usually it takes several minutes to fully launch services
10. `make configure-keycloak` - configures keycloak
11. `make init-dataspace` - configures identity-hub 
12. `make verify-dataspace`


## How It Works

- `deploy.yaml` triggers subsequent playbooks.
- `deploy-env.yaml` renders `.env` and `.env.secrets` from `vars/shared_vars.yaml` and `vars/secrets.yaml` for the scripts under `scripts/`.
- `deploy-secrets.yaml` loads all YAML files from `secrets/` and renders Jinja variables from `vars/shared_vars.yaml` and `vars/secrets.yaml`.
- `deploy-databases.yaml` starts the stateful section components: connector DB, optional Keycloak DB, optional Identity Hub DB, and optional Vault.
- `deploy-stateless-services.yaml` starts connector, dashboard, and optional application services.
- `deploy-routes.yaml` creates routes for proper proxy to specific services.
- `deploy-vault.yaml` allows to run a key-vault only to initialize it for the first time


## Configuration

### Deployment Model

There is one required base and three optional sections.

Required base `connector`:

- connector
- connector DB
- dashboard

Optional sections:

- `identity-provider` = keycloak + keycloak DB
- `identity-hub` = identity-hub + identity-hub DB + Vault
- `storage` = storage + consumer-backend

Set proper values of `enable_identity_provider`, `enable_identity_hub`, `enable_storage` to enable/disable

---

Do not enable only one service from an optional section. The sections are grouped by responsibility, not by image count.

### Provided by a dataspace

Important placeholders to replace with real Data Space values:

- `ISSUER_DID`
- `FEDERATED_CATALOG_ADDRESS`
- `DATASPACE_HUB_URL`
- `CATALOG_API_KEY`
- `DSH_API_KEY` (optional, leave empty if Data Space Hub does not require API key)

Most important fields in [vars/shared_vars.yaml](vars/shared_vars.yaml):

- `k8s_namespace`: namespace for services.
- `connector_id`: connector instance identifier (set once per new connector deployment).
- `participant_id`: automatically generated. Can be overwritten explicitly.
- `public_scheme`: public address scheme (http or https).
- `hosts` section: host addresses for Ingress.
- `is_auth`: enables/disables token-based auth for connector APIs (defaults to enabled).


Database service names (default):

- connector DB: <application>-connector-db
- keycloak DB: <application>-keycloak-db
- identity-hub DB: <application>-identity-hub-db

## Secrets

See [secrets/README.md](secrets/README.md) for detailed examples and templates.

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
## Verification

After deployment, you can check the status of resources:

```bash
kubectl -n <namespace> get deploy,svc,ingress
```

## Notes

- Required section is always deployed; optional sections are controlled by `enable_identity_provider`, `enable_identity_hub`, and `enable_storage`.
- Databases and storage are deployed as StatefulSets because they own persistent data; a standalone PVC is just storage allocation and not a workload controller.
- Vault deployment covers Kubernetes resources only. Vault initialization, unseal, and secret bootstrap still require an explicit operational step after deployment.
- Storage and consumer-backend services are created when `enable_storage=true`.
- Images come from Docker Hub: `psncedcmvds/connector`, `psncedcmvds/data-dashboard`, `psncedcmvds/consumer-backend`, `psncedcmvds/identity-hub`.
- Templates in `templates/*.yaml` are rendered by Ansible (they contain Jinja `{% if %}` blocks).

Critical note:
Those instructions were run for a full-deployment. If you want to launch only some of the services, you have to disable/enable desired ones and then provide proper hosts/addresses/secrets for services that are not deployed by your organization but you want to use. 

Operational note:
This deployment creates Vault pods and persistent storage, but it does not automate `vault operator init`, unseal, or secret seeding.

Secret values should be maintained centrally in [vars/secrets.yaml](vars/secrets.yaml) and referenced from secret manifests with `{{ secrets.<service>.<key> }}`.

Secret values should be maintained centrally in [vars/secrets.yaml](vars/secrets.yaml) and referenced from secret manifests with `{{ secrets.<service>.<key> }}`.

Critical note:
Different services must contain matching credentials as they share components or use each others. If they diverge, the section deploys but does not work.

Data Space note:
Fill `issuer_did`, `federated_catalog_address`, `data_space_hub_address`, and optionally `dsh_api_key` in `vars/shared_vars.yaml`. If DSH does not require API key, keep `dsh_api_key` empty.

## Practical Rules

- If a participant does not need login and realm management, disable `identity-provider`.
- If a participant does not need Identity Hub APIs and Vault-backed secret material, disable `identity-hub`.
- If a participant does not need internal S3-compatible storage for transfers, disable `storage`.
- Keep section ownership strict. Do not move services between sections just because two images happen to talk to each other.

### FAQ & debugging