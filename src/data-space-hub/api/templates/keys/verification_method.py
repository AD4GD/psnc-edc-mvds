TEMPLATE = """
{
    "id": {issuer_key_id},
    "type": "JsonWebKey2020",
    "controller": {issuer},
    "publicKeyMultibase": null,
    "publicKeyJwk": {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": {key_hash}
    }
}
"""
