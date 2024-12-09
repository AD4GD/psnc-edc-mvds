ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG JVM_ARGS=""

RUN apt update \
    && apt install -y curl \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

WORKDIR /app

# Copy the source code
COPY src/registration-service-backend/ /app/

# Ensure the Gradle wrapper is executable
RUN chmod +x /app/gradlew

# Build the project inside the container
RUN ./gradlew launcher:build --no-daemon
ENV CONNECTOR_BUILD_PATH=/app/launcher/build/libs/app.jar
# Copy the built JAR to /app/app.jar
RUN cp $CONNECTOR_BUILD_PATH /app/app.jar

RUN touch /app/empty-vault.properties
RUN mkdir /app/config
COPY ./docker/registration-service-backend/config/* /app/config/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Use "exec" for graceful termination (SIGINT) to reach JVM.
# ARG can not be used in ENTRYPOINT so storing values in ENV variables
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar /app/app.jar"]
