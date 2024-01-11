ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG JVM_ARGS=""

RUN apt update \
    && apt install -y curl \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

WORKDIR /app

COPY ./docker/connector/build/libs/connector.jar /app/app.jar
RUN touch /app/empty-vault.properties
RUN mkdir /app/config
RUN mkdir /app/certs
COPY ./docker/connector/config/* /app/config/
COPY ./docker/connector/certs/* /app/certs/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Use "exec" for graceful termination (SIGINT) to reach JVM.
# ARG can not be used in ENTRYPOINT so storing values in ENV variables
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT [ "sh", "-c", \
    "exec java $JVM_ARGS -jar app.jar"]
