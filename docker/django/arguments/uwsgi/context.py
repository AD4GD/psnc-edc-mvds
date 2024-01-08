context.groups(
    Group(
        SRV_DJANGO_PORT=9001,
        SRV_UWSGI_PROCESSES=4,
        SRV_UWSGI_LISTEN=128,
        # the default value SRV_UWSGI_GEVENT here should be kept in sync
        # with default values in:
        # src/main/settings.py
        # src/main/wsgi.py
        SRV_UWSGI_GEVENT=True,
        SRV_UWSGI_GEVENT_CORES=16,
        SRV_UWSGI_HARAKIRI=True,
        SRV_UWSGI_HARAKIRI_TIMEOUT=120,
        SRV_UWSGI_KEEP_ALIVE=True,
        SRV_UWSGI_KEEP_ALIVE_TIMEOUT=60,
        # The internal uwsgi default is 30, which proved to be low many times
        # by causing
        # [uwsgi-body-read] Timeout reading XXXX bytes.
        # error.
        # 60 seconds proved to better default, although 120 was also used in some-cases.
        # However, it should not be increased without consideration.
        SRV_UWSGI_SOCKET_TIMEOUT=60,
        SRV_UWSGI_BUFFER_SIZE=8192,
        # This parameter is for all options not directly represented above.
        # This is a plain list, not a dict, because not all uwsgi options
        # have values, some are passed without value.
        # Passing SRV_UWSGI_EXTRA_OPTIONS=some-option=value,some-other-option
        # will generate following lines in uwsgi.ini:
        # some-option=value
        # some-other-option
        SRV_UWSGI_EXTRA_OPTIONS=[],
    )
)

context.glob_templates("/var/run/uwsgi", "*.ini")


@context.postprocess
def postprocess(variables, extra):
    extra.update(dict())
