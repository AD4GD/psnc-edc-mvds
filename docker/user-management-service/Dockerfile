ARG BASE_IMAGE
FROM ${BASE_IMAGE}
# FROM python:3.13-alpine

ENV PROJECT_PATH="src/user-management-service"
ENV DOCKER_PATH="../docker/user-management-service"

RUN apk update \
    && apk add --no-cache mesa-gl glib make

WORKDIR /app

COPY $PROJECT_PATH/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY $PROJECT_PATH/api/ /app/api/
COPY $PROJECT_PATH/alembic/ /app/alembic/
COPY $PROJECT_PATH/Makefile /app/Makefile
COPY $PROJECT_PATH/alembic.ini /app/alembic.ini

COPY $DOCKER_PATH/config/configuration.properties /app/.env
COPY $DOCKER_PATH/entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Use entrypoint.sh as container entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
