TEMPLATE = """
{
    "proof": {
        "type": "RsaSignature2018",
        "created": {key_created_date_iso},
        "proofPurpose": "assertionMethod",
        "verificationMethod": {verification_method},
        "jws": {raw_vc_jwt}
    }
}
"""
