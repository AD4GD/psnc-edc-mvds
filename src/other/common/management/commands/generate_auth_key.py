import json

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text
from jose import jwk


class Command(BaseCommand):
    help = "Generate private HMAC key."

    def add_arguments(self, parser):
        parser.add_argument("-s", "--secret", default=settings.SECRET_KEY, help="secret key")
        parser.add_argument("-r", "--random", action="store_true", help="generate random key")
        parser.add_argument("-i", "--issuer", default="default-issuer", help="issuer name")
        parser.add_argument("-k", "--kid", default="default-kid", help="key ID")

    def handle(self, secret, random, issuer, kid, *args, **options):  # pylint: disable=W0613
        key = get_random_string(50) if random else secret

        jwk_key = jwk.HMACKey(key, "HS256")

        jwk_dict = {force_text(k): force_text(v) for k, v in jwk_key.to_dict().items()}
        jwk_dict["kid"] = kid

        jwk_set = {"keys": [jwk_dict]}

        self.stdout.write(json.dumps({issuer: jwk_set}))
