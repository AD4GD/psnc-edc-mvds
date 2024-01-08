from django.conf import settings

from common.auth.base import KeyStore

default_key_store = KeyStore(settings.AUTH_OPENID_PROVIDER)

# add static keys to default key store and cache it forever
for issuer, key_set in settings.AUTH_KEYS.items():
    default_key_store.add_keys(issuer, key_set["keys"], timeout=None)
