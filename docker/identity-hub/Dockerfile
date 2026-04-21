ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# available types: dcp
ARG LAUNCHER_TYPE="dcp"
ARG JVM_ARGS=""
ARG HARICA_CERT_URL="https://repo.harica.gr/certs/HARICA-TLS-Root-2021-RSA.pem"
ARG HARICA_CERT_ALIAS="harica-tls-root-2021-rsa"

ENV PROJECT_PATH="src/identity-hub"
ENV SHARED_EXTENSIONS_PATH="src/shared-extensions"

ENV ORG_GRADLE_PROJECT_persistence=true

# Install required tools
RUN apt update \
    && apt install -y curl unzip \
    && apt clean \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

# Add HARICA CA to JVM truststore for TLS connections to partners using HARICA-issued certs.
RUN curl -fsSL -o /tmp/harica.pem "$HARICA_CERT_URL" \
    && keytool -importcert \
        -noprompt \
        -cacerts \
        -alias "$HARICA_CERT_ALIAS" \
        -storepass changeit \
        -file /tmp/harica.pem \
    && rm -f /tmp/harica.pem

WORKDIR /app

# Create gradlew caching layer
COPY $PROJECT_PATH/gradlew /app/
COPY $PROJECT_PATH/gradle /app/gradle
RUN chmod +x /app/gradlew
# Cache gradlew wrapper
RUN ./gradlew init
RUN ./gradlew wrapper

# Publish local maven packages
WORKDIR /libs
COPY $SHARED_EXTENSIONS_PATH/ /libs/
RUN chmod +x /libs/gradlew
RUN ./gradlew publishToMavenLocal

WORKDIR /app

# Copy the remaining source code
COPY $PROJECT_PATH/ /app/

# Fix permissions
RUN chmod +x /app/gradlew

# Copy dependencies
RUN ./gradlew dependencies

# Build the project
RUN ./gradlew launchers:$LAUNCHER_TYPE:build

# Define the path to the built JAR
ENV APP_BUILD_PATH=/app/launchers/$LAUNCHER_TYPE/build/libs/identity-hub.jar

# Copy the built JAR
RUN cp $APP_BUILD_PATH /app/app.jar

# Create directories and copy configurations
RUN mkdir /app/certs
COPY ./docker/identity-hub/config/* /app/config/
COPY ./docker/identity-hub/certs/* /app/certs/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Define the entrypoint
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar /app/app.jar" ]