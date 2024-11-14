import logging

import requests
from django.conf import settings
from django.core.cache import caches
from django.core.signing import BadSignature
from jose import jwk, jws, jwt

logger = logging.getLogger(__name__)


class TokenGetter:
    def __init__(self, error_handler):
        self.error = error_handler

    def get_token(self, request):
        raise NotImplementedError


class TokenHeaderGetter(TokenGetter):
    header_name = settings.AUTH_HEADER_NAME
    header_prefix = settings.AUTH_HEADER_PREFIX

    def get_token(self, request):
        auth = request.META.get("HTTP_{}".format(self.header_name.upper()))

        if not auth:
            return None

        if " " not in auth:
            return self.error("Missing authorization header prefix.")

        prefix, token = auth.split(maxsplit=1)

        if prefix != self.header_prefix:
            return self.error("Invalid authorization header prefix.")

        return token


class TokenCookieGetter(TokenGetter):
    cookie_name = settings.AUTH_COOKIE_NAME

    def get_token(self, request):
        try:
            return request.get_signed_cookie(self.cookie_name)
        except KeyError:
            return None
        except BadSignature as e:
            return self.error("Error decoding cookie: {}".format(e), e)


class TokenPostGetter(TokenGetter):
    field_name = "token"

    def get_token(self, request):
        return request.POST.get(self.field_name)


class TokenHandler:
    required_claims = settings.AUTH_REQUIRED_CLAIMS + [
        settings.AUTH_SUBJECT_CLAIM,
    ]

    def __init__(self, token_getter_classes, key_store=None):
        self.token_getters = [cls(self.error) for cls in token_getter_classes]
        self._key_store = key_store
        self.context = {}

    def process(self, request, context=None):
        token = self.get_token(request)

        if not token:
            return None

        return self.decode(token, context)

    def get_token(self, request):
        for getter in self.token_getters:
            token = getter.get_token(request)
            if token is not None:
                return token

        return None

    def get_decode_args(self, token):
        try:
            header = jws.get_unverified_header(token)
        except jwt.JWSError as e:
            return self.error("Error decoding token header: {}".format(e), e)

        kid = header.get("kid")

        if kid is None:
            return self.error("Missing 'kid' attribute in token header.")

        result = self.key_store.get(kid)

        if result is None:
            return self.error("Unknown Key ID, not associated with any key definition.")

        return result

    @property
    def key_store(self):
        return self._key_store

    def decode(self, token, context=None):
        self.context = context or {}

        issuer, key = self.get_decode_args(token)

        decode_additional_kwargs = dict()
        decode_additional_options = {"verify_aud": bool(settings.AUTH_AUD), "leeway": settings.AUTH_LEEWAY}

        if decode_additional_options["verify_aud"]:
            decode_additional_kwargs["audience"] = settings.AUTH_AUD
            decode_additional_options["require_aud"] = True

        try:
            claims = jwt.decode(
                token, key, issuer=issuer, options=decode_additional_options, **decode_additional_kwargs
            )
        except jwt.JWTError as e:
            return self.error("Error decoding token: {}".format(e), e)

        self.validate_claims(claims)

        return claims

    def validate_claims(self, claims):
        for claim in self.required_claims:
            if claim not in claims:
                self.error("Missing '{}' claim.".format(claim))

    def error(self, message, exc=None):
        raise ValueError(message)


class KeyStore:
    cache = caches[settings.AUTH_KEYSTORE_CACHE]

    def __init__(self, openid_provider=None):
        self.openid_provider = openid_provider

    def _cache_key(self, kid):
        return "kid:{}:{}".format(self.openid_provider, kid)

    def add(self, kid, issuer, key, timeout):
        self.cache.set(self._cache_key(kid), (issuer, key), timeout)

    def get(self, kid):
        key = self._cache_key(kid)
        value = self.cache.get(key)

        if value is not None:
            return value

        if self.openid_provider:
            self.openid_discovery(self.openid_provider)

            return self.cache.get(key)

        return None

    def openid_discovery(self, openid_provider):
        def request_json_field(url, field):
            response = requests.get(url, timeout=settings.AUTH_REQUESTS_TIMEOUT, verify=settings.AUTH_REQUESTS_VERIFY)
            response.raise_for_status()

            value = response.json().get(field)

            if value is None:
                raise ValueError("Field '{}' not found in the response for: {}.".format(field, url))

            return value

        logger.info("Starting discovery for OP {}.".format(openid_provider))

        discovery_url = openid_provider
        if not discovery_url.endswith("/"):
            discovery_url += "/"
        discovery_url += ".well-known/openid-configuration"

        try:
            jwks_uri = request_json_field(discovery_url, "jwks_uri")
            keys = request_json_field(jwks_uri, "keys")
        except (requests.RequestException, ValueError) as e:
            logger.error("Error requesting discovery endpoint: {}".format(e))
            return 0

        return self.add_keys(openid_provider, keys, settings.AUTH_KEYSTORE_TIMEOUT)

    def add_keys(self, issuer, keys, timeout):
        count = 0
        for key in keys:
            if not isinstance(key, dict):
                logger.warning("Invalid key type.")
                continue

            # try to construct key to validate it
            try:
                kid = key["kid"]
                jwk.construct(key)
            except KeyError:
                logger.warning("Key definition doesn't contain 'kid' field.")
                continue
            except jwk.JWKError as e:
                logger.warning("Error constructing key: {}".format(e))
                continue

            self.add(kid, issuer, key, timeout)
            logger.info("Successfully added key with kid='{}' from {}.".format(kid, issuer))
            count += 1

        if not count:
            logger.warning("No keys were discovered for OP {}.".format(issuer))

        return count
