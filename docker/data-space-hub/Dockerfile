ARG BASE_IMAGE
FROM ${BASE_IMAGE}
# FROM python:3.13-alpine

RUN apk update \
    && apk add --no-cache mesa-gl glib make

WORKDIR /app

COPY src/data-space-hub/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src/data-space-hub/api/ /app/api/
COPY src/data-space-hub/alembic/ /app/alembic/
COPY src/data-space-hub/Makefile /app/Makefile
COPY src/data-space-hub/alembic.ini /app/alembic.ini

COPY ../docker/data-space-hub/config/config.properties /app/.env
COPY ../docker/data-space-hub/entrypoint.sh /app/entrypoint.sh
