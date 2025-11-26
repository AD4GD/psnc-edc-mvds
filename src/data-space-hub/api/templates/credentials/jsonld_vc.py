TEMPLATE = """
{
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://w3id.org/security/suites/jws-2020/v1",
        "https://www.w3.org/ns/did/v1",
        "https://www.w3.org/TR/vc-data-model/",
        {context_for}
    ],
    "id": {credential_id},
    "credentialSchema": {credential_schema},
    "credentialStatus": {credential_status},
    "credentialSubject": {
        "id": {user_did},
        "contractVersion": {contract_version},
        "claims": {claims},
        "level": {processing_level}
    },
    "description": {description},
    "issuanceDate": {issuance_date_iso},
    "expirationDate": {expiration_date_iso},
    "issuer": {issuer},
    "name": {name},
    "type": {list_of_credential_types}
}
"""
