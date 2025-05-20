FROM alpine:latest

WORKDIR /home/app
RUN apk update && \
apk add --no-cache bash curl jq openssl perl-utils
COPY . ./
RUN chmod +x entrypoint.sh

# ENTRYPOINT [ "./entrypoint.sh" ]
