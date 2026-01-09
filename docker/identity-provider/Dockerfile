ARG BASE_IMAGE
ARG KC_VERSION=24.0.3
FROM ${BASE_IMAGE} AS admin-ext-builder

WORKDIR /app

COPY src/keycloak/pom.xml ./pom.xml
COPY src/keycloak/src ./src

RUN mvn -Dversion.keycloak=${KC_VERSION} clean package

FROM quay.io/keycloak/keycloak:${KC_VERSION}

COPY --from=admin-ext-builder \
  /app/target/admin-approval-listener-1.0.0.jar \
  /opt/keycloak/providers/admin-approval-listener-1.0.0.jar

RUN /opt/keycloak/bin/kc.sh build

CMD ["start"]
