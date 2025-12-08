TEMPLATE = """
{
    "iss": {issuer},
    "aud": {participant_did},
    "sub": {participant_did},
    "vc": {vc},
    "iat": {issued_at},
    "exp": {expires_at},
    "metadata": {metadata_vc}
}
"""
