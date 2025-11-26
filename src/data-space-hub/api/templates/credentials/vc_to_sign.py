TEMPLATE = """
{
    "iss": {issuer},
    "aud": {user_did},
    "sub": {user_did},
    "vc": {vc},
    "iat": {issued_at},
    "exp": {expires_at},
    "metadata": {metadata_vc}
}
"""
