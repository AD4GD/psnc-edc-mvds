TEMPLATE = """
{
    "service": [],
    "verificationMethod": {list_of_verification_methods},
    "authentication": {list_of_key_ids},
    "id": {issuer},
    "@context": [
        "https://www.w3.org/ns/did/v1",
        {
            "@base": {issuer}
        }
    ]
}
"""
