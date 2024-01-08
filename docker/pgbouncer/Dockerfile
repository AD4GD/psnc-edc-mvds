ARG BUILDER_IMAGE
ARG BASE_IMAGE

FROM ${BUILDER_IMAGE} AS build_stage
FROM ${BASE_IMAGE}

# explicitly set user/group IDs
RUN set -eux; \
	addgroup -S pgbouncer; \
	adduser -S -G pgbouncer -u 999 -h /var/lib/pgbouncer -s /bin/ash pgbouncer; \
	# needed to run a container as any user
	chown :0 /var/lib/pgbouncer; \
	chmod g=u /var/lib/pgbouncer

RUN apk --update add libevent openssl-dev c-ares

COPY --from=build_stage /pgbouncer /usr/local

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

USER 999
EXPOSE 6432
CMD ["pgwrapper"]
