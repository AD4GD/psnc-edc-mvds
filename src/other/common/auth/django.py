from functools import wraps

from django.http import JsonResponse
from django.utils.functional import SimpleLazyObject

from common.auth import base, default_key_store


class TokenAuthenticationMiddleware:
    handler_class = base.TokenHandler
    getter_classes = [base.TokenHeaderGetter, base.TokenCookieGetter]

    def __init__(self, get_response):
        self.get_response = get_response

        self.handler = self.handler_class(self.getter_classes, default_key_store)

    def __call__(self, request):
        request.claims = SimpleLazyObject(lambda: self.get_claims(request))

        return self.get_response(request)

    def get_claims(self, request):
        # pylint: disable=W0212
        if not hasattr(request, "_cached_claims"):
            try:
                request._cached_claims = self.handler.process(request)
            except ValueError:
                request._cached_claims = None

        return request._cached_claims


def token_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.claims:
            return JsonResponse({"message": "Missing or invalid authentication token."}, status=401)

        return view(request, *args, **kwargs)

    return wrapper
