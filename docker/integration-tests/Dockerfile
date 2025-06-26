FROM alpine:latest

WORKDIR /home/app
RUN apk update && \
apk add --no-cache bash curl jq 
COPY . ./
RUN chmod +x entrypoint.sh

SHELL [ "/bin/bash", "-c" ]
