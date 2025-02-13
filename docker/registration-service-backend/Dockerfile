ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG JVM_ARGS=""

ENV PROJECT_PATH="src/registration-service-backend"
ENV SHARED_EXTENSIONS_PATH="src/shared-extensions"

# Install required tools
RUN apt update \
    && apt install -y curl unzip \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

WORKDIR /app

# Create gradlew caching layer
COPY $PROJECT_PATH/gradlew /app/
COPY $PROJECT_PATH/gradle /app/gradle
RUN chmod +x /app/gradlew
# Need for gradlew wrapper
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
RUN ./gradlew launcher:build --no-daemon

# Define the path to the built JAR
ENV APP_BUILD_PATH=/app/launcher/build/libs/app.jar

# Copy the built JAR
RUN cp $APP_BUILD_PATH /app/app.jar

# Create directories and copy configurations
RUN touch /app/empty-vault.properties \
    && mkdir /app/config
COPY ./docker/registration-service-backend/config/* /app/config/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Use "exec" for graceful termination (SIGINT) to reach JVM.
# ARG can not be used in ENTRYPOINT so storing values in ENV variables
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar /app/app.jar"]
