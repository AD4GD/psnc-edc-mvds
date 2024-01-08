"""
WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from . import patches


# this is redundancy of django.conf settings
def is_true(name):
    return os.environ.get(name, "").lower() in {"true", "on", "ok", "y", "yes", "1"}


# the default value SRV_UWSGI_GEVENT here should be kept in sync
# with default values in:
# docker/django/arguments/uwsgi/context.py
# src/main/settings.py
SRV_UWSGI_GEVENT = is_true("SRV_UWSGI_GEVENT")
_SRV_RUNNING_INSIDE_UWSGI = is_true("_SRV_RUNNING_INSIDE_UWSGI")

if SRV_UWSGI_GEVENT and _SRV_RUNNING_INSIDE_UWSGI:
    patches.patch_gevent(with_check=True)
    patches.patch_gevent_psycopg()


# this import has to be here after above code, otherwise settings would be loaded to
# early
from django.core.wsgi import get_wsgi_application  # pylint: disable=C0413,C0411 # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

application = get_wsgi_application()

if _SRV_RUNNING_INSIDE_UWSGI:
    application = patches.patch_uwsgi_reason_phrase_logging(application)
else:
    patches.patch_runserver_reason_phrase_logging()
