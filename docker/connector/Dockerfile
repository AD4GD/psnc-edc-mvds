ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# available types: daps, no-daps
ARG LAUNCHER_TYPE="daps"
ARG JVM_ARGS=""

ENV PROJECT_PATH="src/edc-connector"
ENV SHARED_EXTENSIONS_PATH="src/shared-extensions"

# Install required tools
RUN apt update \
    && apt install -y curl unzip \
    && apt clean \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

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
RUN ./gradlew publishToMavenLocal --no-daemon

WORKDIR /app

# Copy the remaining source code
COPY $PROJECT_PATH/ /app/

RUN chmod +x /app/gradlew

# Build the project
RUN ./gradlew launchers:$LAUNCHER_TYPE:build --no-daemon

# Define the path to the built JAR
ENV APP_BUILD_PATH=/app/launchers/$LAUNCHER_TYPE/build/libs/connector.jar

# Copy the built JAR
RUN cp $APP_BUILD_PATH /app/app.jar

# Create directories and copy configurations
RUN touch /app/empty-vault.properties \
    && mkdir /app/config /app/certs
COPY ./docker/connector/config/* /app/config/
COPY ./docker/certs/* /app/certs/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Define the entrypoint
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar /app/app.jar" ]