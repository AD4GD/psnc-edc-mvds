template = """
{
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://w3id.org/security/suites/jws-2020/v1",
        "https://www.w3.org/ns/did/v1",
        "https://www.w3.org/TR/vc-data-model/",
        {
            "mvd-credentials": "https://w3id.org/mvd/credentials/",
            "contractVersion": "mvd-credentials:contractVersion",
            "level": "mvd-credentials:level"
        }
    ],
    "id": {credential_id},
    "type": [
        "VerifiableCredential",
        "DataProcessorCredential"
    ],
    "issuer": {issuer},
    "issuanceDate": {issuance_date_iso},
    "expirationDate": {expiration_date_iso},
    "credentialSubject": {
        "id": {user_did},
        "contractVersion": {contract_version},
        "level": {processing_level},
        "claims": {claims}
    }
}
"""
