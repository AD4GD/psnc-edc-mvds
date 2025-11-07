ARG BASE_IMAGE
FROM ${BASE_IMAGE}
# FROM python:3.13-alpine

RUN apk update \
    && apk add --no-cache mesa-gl glib make

WORKDIR /app

COPY src/mail-service/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src/mail-service/* /app/

COPY ../docker/mail-service/config/config.properties /app/.env
