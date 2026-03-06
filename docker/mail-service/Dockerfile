ARG BASE_IMAGE
FROM ${BASE_IMAGE}
# FROM python:3.13-alpine

RUN apk update \
    && apk add --no-cache mesa-gl glib make

WORKDIR /app

COPY src/mail-service/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src/mail-service/* /app/

COPY ../docker/mail-service/config/configuration.properties /app/.env
COPY ../docker/mail-service/entrypoint.sh /app/entrypoint.sh
RUN chmod 0755 /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]