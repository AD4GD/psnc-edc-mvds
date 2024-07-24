#
#    Copyright 2024 sovity GmbH
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#    SPDX-License-Identifier: Apache-2.0
#

ARG KC_VERSION=24.0.3

FROM maven:3-eclipse-temurin-17 AS daps-ext-builder
ARG KC_VERSION

WORKDIR /home/app
COPY . ./
RUN --mount=type=cache,target=/root/.m2 mvn -D "version.keycloak=${KC_VERSION}" clean package

FROM quay.io/keycloak/keycloak:${KC_VERSION}
COPY --from=daps-ext-builder /home/app/target/dat-extension.jar /opt/keycloak/providers/dat-extension.jar

# Theme Customization
COPY themes/ /opt/keycloak/themes/

CMD ["start"]
