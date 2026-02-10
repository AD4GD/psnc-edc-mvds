TEMPLATE = """
{
  "credentialSubject": [
    {credential_props}
  ],
  "id": {vc_id},
  "type": [
    "VerifiableCredential",
    {credential_type}
  ],
  "issuer": {
    "id": {issuer_did},
    "additionalProperties": {}
  },
  "issuanceDate": {issuance_date},
  "expirationDate": null,
  "credentialStatus": null,
  "description": null,
  "name": null
}
"""