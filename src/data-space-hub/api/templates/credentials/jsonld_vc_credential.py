TEMPLATE = """
{
  "credentialSubject": [
    {credential_props}
  ],
  "id": "http://org.yourdataspace.com/credentials/1265",
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