TEMPLATE = """
{
    "iss": {issuer},
    "aud": {connector_did},
    "sub": {connector_did},
    "vc": {vc},
    "iat": {issued_at},
    "exp": {expires_at},
    "metadata": {metadata_vc}
}
"""
