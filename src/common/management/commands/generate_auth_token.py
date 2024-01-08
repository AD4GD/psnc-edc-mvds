import hashlib
import json

from django.conf import settings
from django.core.management import BaseCommand

from common.utils import generate_token


class Command(BaseCommand):
    help = "Generate authorization token."

    def add_arguments(self, parser):
        parser.add_argument("subject", help="token subject")
        parser.add_argument("-s", "--secret", default=settings.SECRET_KEY, help="secret key")
        parser.add_argument("-i", "--issuer", default=settings.MAIN_DOMAIN, help="issuer name")
        parser.add_argument(
            "-k", "--kid", default=hashlib.sha512(settings.SECRET_KEY.encode()).hexdigest()[:40], help="key ID"
        )
        parser.add_argument("-t", "--timeout", type=int, default=60 * 60 * 24 * 100, help="token timeout")
        parser.add_argument("-c", "--claims", help="extra claims in json format")

    def handle(self, secret, issuer, kid, subject, timeout, claims, **options):  # pylint: disable=R0913,W0613
        default_claims = {
            settings.AUTH_SUBJECT_CLAIM: subject,
        }
        if claims:
            default_claims.update(json.loads(claims))

        self.stdout.write(generate_token(issuer, kid, secret, timeout, "HS256", **default_claims))
