## Intro
This repository contains the source code of all components required by Minimum Viable Dataspace (MVD).

Current MVD solution utilizes **Dataspace Protocol (DCP)** for establishing trust between the participants.

The project is based on PSNC skeletons, and has the following structure:
- `/src` (source code of each component, see below for the full list)
- `/src/notebooks` (Jupyter notebooks for manual testing and integration verification)
- `/docker` (dockerfiles and configuration files)
- `/compose` (local docker compose files)
- `/bin` (contains scripts for local development)
- `/deployment` (ansible playbooks responsible for the deployment)
- `/deployment/instructions` (step-by-step guides on how to deploy the solution on your own infrastructure on VM OR K8s cluster)

## Components
The full and up-to-date list of components can be found in the `/src` directory. Key components include:

- connector (based on EDC v0.14.0)
- data-dashboard (compatible with EDC v0.14.0)
- federated-catalog (based on EDC v0.14.0)
- identity-hub (based on EDC v0.14.0)
- data-space-hub
- data-space-portal
- consumer-backend
- mail-service

## Build & Run locally
Build images
1. `cd ./docker`
2. `make build` (rebuild single service `make build-<service-name>`)

Run the images locally
1. `cd ./bin`
2. `./devstack up` (restart single service e.g. after rebuild `./devstack up -d --force-recreate <service-name>`)

First `./devstack up` run will require to enter `REPO_DIR` (path to the project) and `REGISTRY_DOMAIN` (docker container registry domain).

## Tests
Currently there are implemented integration tests but no unit tests. Integration tests are run everytime during pipeline phase. They check operability of services and the connection between them. Components can also be manually tested via Jupyter notebooks located in `/src/notebooks`.

## Deploy
Deployment is managed via Ansible playbooks located in `/deployment`. For instructions on how to deploy the solution on your own infrastructure, refer to the `/deployment/instructions` directory.

We have three operational deployments located on the `bst2` PSNC cluster:

- **Demonstrational deployment** - intended for showcase and demonstration purposes
- **Project deployment #1** - used for conducting tests and pilots within SAGE project scope
- **Project deployment #2** - used for conducting tests and pilots within CEADS project scope