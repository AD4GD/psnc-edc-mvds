## Intro
This repository contains the source code of all components required by Minimum Viable Dataspace (MVD).

Current MVD solution utilizes OAuth 2.0 implemented with Dynamic Attribute Provisioning Service (DAPS) for establishing trust between the participants.

The project is based on PSNC skeletons, and has the following structure:
- `/src` (source code of each component)
- `/docker` (dockerfiles and configuration files)
- `/compose` (local docker compose files)
- `/bin` (contains scripts for local development)
- `/deployment` (ansible playbooks responsible for the deployment)

## Components
- connector (based on EDC v0.10.1)
- data-dashboard (compatible with EDC v0.10.1)
- federated-catalog (based on EDC v0.10.1)
- consumer-backend
- registration-service-backend (under development)
- registration-service-frontend (under development)

## Build & Run locally
Build images
1. `cd ./docker`
2. `make build`

Run the images locally
1. `cd ./bin`
2. `./devstack up`

First `./devstack up` run will require to enter `REPO_DIR` (path to the project) and  `REGISTRY_DOMAIN` (docker container registry domain).

## Tests
Currently there are no unit or integration tests. Connector and other components of the dataspace can be manually tested via running jupyter notebooks. 

## Deploy
We have two operational deployments located on different Kubernetes clusters.

- The first deployment is located on the `paas-dev` PSNC cluster and is intended for demonstrational purposes.
- The second deployment is located on the `dcw1` PSNC cluster. It's used for conducting tests and pilots in terms of D4.X deliverables. 