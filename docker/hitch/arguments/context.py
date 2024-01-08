context.groups(
    Group(
        HITCH_LISTENING_ADDRESS=GenericUrl("0.0.0.0:443"),
        HITCH_BACKEND_ADDRESS=GenericUrl("0.0.0.0:9003"),
        HITCH_PEM_FILE="/etc/certs/certificate.pem",
        HITCH_PROXY_PROXY=False,
        HITCH_WRITE_PROXY_V1=False,
        HITCH_WRITE_PROXY_V2=False,
        HITCH_QUIET=True,
    )
)

context.glob_templates("/var/run/hitch", "hitch.cfg")
