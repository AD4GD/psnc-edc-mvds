from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import caches
from django.core.checks import Error, register
from watchman.decorators import check


@check
def django():
    return {"django": {"ok": True}}

@register(deploy=True)
def gevent_default_database(app_configs, **kwargs):  # pylint: disable=W0613
    errors = []

    if settings.SRV_UWSGI_GEVENT:
        default_database = settings.DATABASES.get("default")

        if default_database is not None and default_database["ENGINE"] != "django.db.backends.postgresql_psycopg2":
            errors.append(Error("when SRV_UWSGI_GEVENT is true, only postgres backend is supported"))

    return errors
