import hashlib

from django.apps import AppConfig
from django.conf import settings

from common.auth import default_key_store


class CommonConfig(AppConfig):
    name = "common"

    def ready(self):
        # add key based on app secret to the default key store and cache it forever
        if settings.AUTH_ADD_SECRET_KEY:
            secret = settings.SECRET_KEY
            kid = hashlib.sha512(secret.encode()).hexdigest()[:40]
            issuer = settings.MAIN_DOMAIN

            default_key_store.add(kid, issuer, secret, timeout=None)
