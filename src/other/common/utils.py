from datetime import datetime, timedelta

from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt


def generate_private_rsa_key_pem(bits=2048, exponent=65537):
    rsa_key = rsa.generate_private_key(key_size=bits, public_exponent=exponent, backend=crypto_default_backend())

    return rsa_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def generate_token(issuer, kid, key, timeout=300, algorithm="RS256", **claims):
    iat = datetime.now()

    payload = {
        "iss": issuer,
        "iat": iat,
        "nbf": iat,
        "exp": iat + timedelta(seconds=timeout),
    }
    payload.update(claims)

    return jwt.encode(payload, key, algorithm=algorithm, headers={"kid": kid})
