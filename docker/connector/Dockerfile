ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG JVM_ARGS=""

RUN apt update \
    && apt install -y curl \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

WORKDIR /app

COPY ./docker/connector/build/libs/connector.jar /app
RUN mkdir /connector
COPY ./docker/connector/* /connector/
RUN mkdir /certs
COPY ./docker/connector/certs/* /certs/

EXPOSE 29191
EXPOSE 29193
EXPOSE 29194
EXPOSE 29291
EXPOSE 29192

HEALTHCHECK --interval=5s --timeout=5s --retries=10 CMD curl --fail http://localhost:29191/api/check/health

# Use "exec" for graceful termination (SIGINT) to reach JVM.
# ARG can not be used in ENTRYPOINT so storing values in ENV variables
ENV JVM_ARGS=$JVM_ARGS
ENTRYPOINT java $JVM_ARGS -jar connector.jar
