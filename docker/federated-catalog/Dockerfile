ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# available types: catalog-base
ARG LAUNCHER_TYPE="catalog-base"

ARG JVM_ARGS=""

RUN apt update \
    && apt install -y curl \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

WORKDIR /app

# Copy the source code
COPY src/federated-catalog/ /app/

# Ensure the Gradle wrapper is executable
RUN chmod +x /app/gradlew

# Build the project inside the container
RUN ./gradlew launchers:$LAUNCHER_TYPE:build --no-daemon
ENV CONNECTOR_BUILD_PATH=/app/launchers/$LAUNCHER_TYPE/build/libs/fc.jar
# Copy the built JAR to /app/app.jar
RUN cp $CONNECTOR_BUILD_PATH /app/app.jar

RUN touch /app/empty-vault.properties
RUN mkdir /app/config
RUN mkdir /app/certs
COPY ./docker/federated-catalog/config/* /app/config/
#COPY ./docker/federated-catalog/certs/* /app/certs/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Use "exec" for graceful termination (SIGINT) to reach JVM.
# ARG can not be used in ENTRYPOINT so storing values in ENV variables
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar /app/app.jar"]
