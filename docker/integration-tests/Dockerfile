FROM alpine:latest

WORKDIR /home/app
RUN apk update && \
apk add --no-cache bash curl jq uuidgen iputils-ping
COPY . ./
RUN chmod +x entrypoint.sh
