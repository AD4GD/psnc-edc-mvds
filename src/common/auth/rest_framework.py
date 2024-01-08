from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from common.auth import base, default_key_store


class TokenAuthentication(BaseAuthentication):
    handler_class = base.TokenHandler
    getter_classes = [base.TokenHeaderGetter, base.TokenCookieGetter]
    www_authenticate_value = settings.AUTH_HEADER_PREFIX
    subject_claim = settings.AUTH_SUBJECT_CLAIM

    def __init__(self):
        self.handler = self.handler_class(self.getter_classes, default_key_store)

    def authenticate(self, request):
        try:
            claims = self.handler.process(request, context=self.get_handler_context(request))
        except ValueError as e:
            raise AuthenticationFailed(str(e)) from e

        if not claims:
            return None

        return self.get_user(claims), self.get_auth(claims)

    def authenticate_header(self, request):  # pylint: disable=W0613
        return self.www_authenticate_value

    @staticmethod
    def get_handler_context(request):  # pylint: disable=W0613
        return None

    def get_user(self, claims):
        return claims[self.subject_claim]

    def get_auth(self, claims):
        return claims


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):  # pylint: disable=W0613
        return bool(request.user)
