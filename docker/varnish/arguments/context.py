context.groups(
    Group(
        VARNISH_LISTENING_ADDRESS=GenericUrl("0.0.0.0:9002"),
        VARNISH_LISTENING_PROXY_ADDRESS=GenericUrl("0.0.0.0:9003"),
        VARNISH_CACHE_SIZE="1G",
        MAIN_DOMAIN="localhost.edc.connector",
        DJANGO_HOSTS=[GenericUrl("127.0.0.1:9001")],
        HEALTH_ACLS=['"0.0.0.0"/0'],
        HEALTH_ENABLED=True,
        VARNISH_ADDITIONAL_DAEMON_OPTS="",
        VARNISH_IS_FIRST_HTTP_SERVER=True,
    )
)


@context.filter
def regexed_domain(domain):
    return domain.replace(".", "\\.")


@context.filter
def backend_name(host, prefix):
    return "%s_%s" % (prefix, host["hostname"].replace(".", "_"))


context.glob_templates("/var/run/varnish", "varnish.params")
context.glob_templates("/var/run/varnish", "*.vcl")
