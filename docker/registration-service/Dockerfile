ARG BASE_IMAGE
FROM ${BASE_IMAGE}
# FROM python:3.13-alpine

RUN apk update \
    && apk add --no-cache mesa-gl glib make

WORKDIR /app

COPY src/registration-service/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src/registration-service/api/ /app/api/
COPY src/registration-service/alembic/ /app/alembic/
COPY src/registration-service/Makefile /app/Makefile
COPY src/registration-service/alembic.ini /app/alembic.ini

COPY ../docker/registration-service/config/config.properties /app/.env
COPY ../docker/registration-service/entrypoint.sh /app/entrypoint.sh
