from django.conf import settings
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from common.auth import base, default_key_store


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class CookiefyTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    handler_class = base.TokenHandler
    cookie_name = settings.AUTH_COOKIE_NAME
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            self.handler_class([], default_key_store).decode(token)
        except ValueError as e:
            return Response({"message": str(e)}, status=400)

        response = Response({"message": "Token was placed in the cookie."})
        response.set_signed_cookie(self.cookie_name, token)

        return response


class FlushCookieTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    cookie_name = settings.AUTH_COOKIE_NAME

    def post(self, request):  # pylint: disable=W0613
        response = Response({"message": "Token was flushed from cookie."})
        response.delete_cookie(self.cookie_name)

        return response
