ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG PGBOUNCER_VERSION=pgbouncer_1_9_0

RUN set -eux; \
    apk --update add git py-docutils build-base automake libtool m4 autoconf libevent-dev openssl-dev c-ares-dev; \
    \
    git clone -b $PGBOUNCER_VERSION --single-branch --depth 1 https://github.com/pgbouncer/pgbouncer.git /src; \
    cd /src;\
    git submodule update --init; \
    \
    ./autogen.sh; \
    ./configure --prefix=/pgbouncer; \
    make install
