# https://eclipse-edc.github.io/IdentityHub/openapi/identity-api/#/Verifiable%20Credentials/addCredential

TEMPLATE = """
{
    "id": {credential_id},
    "participantContextId": {user_did},
    "timestamp": {creation_timestamp},
    "issuerId": {issuer_did},
    "holderId": {user_did},
    "state": {state},
    "issuancePolicy": {issuance_policy},
    "reissuancePolicy": {reissuance_policy},
    "verifiableCredential": {
        "rawVc": {raw_vc_jwt},
        "format": {vc_format},
        "credential": {credential_ld}
    }
}
"""
