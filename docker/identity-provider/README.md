<!--
   Copyright 2024 sovity GmbH

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   SPDX-License-Identifier: Apache-2.0
-->

<div align="center">
  <img src="https://raw.githubusercontent.com/sovity/edc-ui/d6242a1b3a8c1393921198ec2ef469da2a7111f7/src/assets/images/sovity_logo.svg" alt="sovity Logo" width="300"/>
</div>

# sovity DAPS

sovity's implementation of the Dynamic Attribute Provisioning Service based on the Keycloak IAM platform.

## Table of Contents

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Getting Started](#getting-started)
- [Realm Configuration](#realm-configuration)
- [Managing Participants](#managing-participants)
- [License](#license)

<!-- TOC end -->

## Getting Started

There is an example deployment using Docker Compose, which will automatically build everything on startup.
To use it, copy the file `.env.example` to `.env`
and assign secure secrets, as described in the file.
This setup uses PostgreSQL; however, any database supported by Keycloak can be used.

The setup is configured for a local deployment using plaintext HTTP on port 8080.
For a production environment behind a TLS-terminating reverse proxy,
the following environment variable adjustments are needed:

- `KC_PROXY=edge`
- `KC_HOSTNAME=keycloak.example.com`

Additionally, the `start-dev` command should be removed from the `docker-compose.yml`.

Further configuration options can be found in the official [Keycloak documentation](https://www.keycloak.org/server/all-config).

## Realm Configuration

For least friction, it is recommended to create a separate realm, commonly named "DAPS".
In this new realm, several modifications to pre-existing global defaults need to be made:

- Change all pre-existing client scopes to type "None"
- Create a new client scope of type "Optional" with name `idsc:IDS_CONNECTOR_ATTRIBUTES_ALL`

If you want to use any service accounts to automate configuration management,
it is best to create them before this point.
If you do it later, you will need to manually reassign at least the `roles` scope to any such clients.

## Managing Participants

Participants are represented as Keycloak service accounts.
These should have the "DAT Mapper", a custom protocol mapper implemented in this project,
configured and assigned to them.

For simple management, it is recommended
to use our [Authority Portal](https://github.com/sovity/authority-portal) project.

## License

Copyright 2024 sovity GmbH
                                                                         
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
                                                                         
    http://www.apache.org/licenses/LICENSE-2.0
                                                                         
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
