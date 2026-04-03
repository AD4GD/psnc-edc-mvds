# Running local docker deployment
This folder contains all necessary scripts to run local docker deployment of PCSS-based dataspace

## Possible commands
### Docker commands
All of below scripts can take arguments that are compatible with `docker compose` 

`./kv` - this script initializes vaults for all the services, Information about vaults is stored in [vaults.json](../compose/vaults.json). If needed it can be configured differently (different vaults). After initialization, all of keys and tokens are saved into [secrets](secrets/) directory to corresponding env files.

`./devstack` - Firstable unseals vaults and then runs all of the services that are specified in [base](../compose/base.yaml), [consumer](../compose/consumer.yaml), [provider](../compose/provider.yaml) yaml files

`./devtests` - used to run the test for a whole application

### Standalone scripts

`compose` used to run docker compose services

`render-secrets-config` - used to render vault secrets and saves to [.generated](../compose/.generated/docker) directory proper configurations of services.

`vault-init-unseal` - used to initialize and unseal vault containers. \
**Initialization** - generates `key shard` and `hvs token` which are later stored in proper env file, unseals vault, creates `secrets engine`