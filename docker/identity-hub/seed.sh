#!/bin/bash

#
#  Copyright (c) 2024 Metaform Systems, Inc.
#
#  This program and the accompanying materials are made available under the
#  terms of the Apache License, Version 2.0 which is available at
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  SPDX-License-Identifier: Apache-2.0
#
#  Contributors:
#       Metaform Systems, Inc. - initial API and implementation
#
#

## Seed identity data to identityhubs
API_KEY="c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="

# add participant "consumer"
echo
echo
echo "Create consumer participant context in IdentityHub"
PEM_CONSUMER=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/consumer_public.pem)
DATA_CONSUMER=$(jq -n --arg pem "$PEM_CONSUMER" '{
           "roles":[],
           "serviceEndpoints":[
             {
                "type": "CredentialService",
                "serviceEndpoint": "http://consumer-ih:7081/api/credentials/v1/participants/ZGlkOndlYjpjb25zdW1lci1paCUzQTcwODM6YWxpY2U=",
                "id": "consumer-credentialservice-1"
             },
             {
                "type": "ProtocolEndpoint",
                "serviceEndpoint": "http://consumer-connector:8082/api/dsp",
                "id": "consumer-dsp"
             }
           ],
           "active": true,
           "participantId": "did:web:consumer-ih%3A7083:alice",
           "did": "did:web:consumer-ih%3A7083:alice",
           "key":{
               "keyId": "did:web:consumer-ih%3A7083:alice#key-1",
               "privateKeyAlias": "key-1",
               "publicKeyPem":"\($pem)"
           }
       }')

# the consumer runtime will need to have the client_secret in its vault as well, so we store it in a variable
# and use the Secrets API (part of Management API) to insert it.
clientSecret=$(curl -s --location 'http://localhost:7082/api/identity/v1alpha/participants/' \
--header 'Content-Type: application/json' \
--header "x-api-key: $API_KEY" \
--data "$DATA_CONSUMER" | jq -r '.clientSecret')
echo $clientSecret

# add client secret to the consumer runtime
SECRETS_DATA=$(jq -n --arg secret "$clientSecret" \
'{
  "@context" : {
    "edc" : "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type" : "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id" : "did:web:consumer-ih%3A7083:alice-sts-client-secret",
  "https://w3id.org/edc/v0.0.1/ns/value": "\($secret)"
}')

curl -sL -X POST http://localhost:8081/api/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"

# add participant "federated catalog"
echo
echo
echo "Create federated catalog participant context in IdentityHub"
PEM_FC=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/fc_public.pem)
DATA_FC=$(jq -n --arg pem "$PEM_FC" '{
           "roles":[],
           "serviceEndpoints":[
             {
                "type": "CredentialService",
                "serviceEndpoint": "http://fc-ih:7101/api/credentials/v1/participants/ZGlkOndlYjpmYy1paCUzQTcxMDM6cGlvdHI=",
                "id": "fc-credentialservice-1"
             },
             {
                "type": "ProtocolEndpoint",
                "serviceEndpoint": "http://federated-catalog:8292/api/dsp",
                "id": "fc-dsp"
             }
           ],
           "active": true,
           "participantId": "did:web:fc-ih%3A7103:piotr",
           "did": "did:web:fc-ih%3A7103:piotr",
           "key":{
               "keyId": "did:web:fc-ih%3A7103:piotr#key-1",
               "privateKeyAlias": "key-1",
               "publicKeyPem":"\($pem)"
           }
       }')

# the fc runtime will need to have the client_secret in its vault as well, so we store it in a variable
# and use the Secrets API (part of Management API) to insert it.
clientSecret=$(curl -s --location 'http://localhost:7102/api/identity/v1alpha/participants/' \
--header 'Content-Type: application/json' \
--header "x-api-key: $API_KEY" \
--data "$DATA_FC" | jq -r '.clientSecret')
echo $clientSecret

# add client secret to the fc runtime
SECRETS_DATA=$(jq -n --arg secret "$clientSecret" \
'{
  "@context" : {
    "edc" : "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type" : "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id" : "did:web:fc-ih%3A7103:piotr-sts-client-secret",
  "https://w3id.org/edc/v0.0.1/ns/value": "\($secret)"
}')

curl -sL -X POST http://localhost:8291/api/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"

# add participant "provider"
echo
echo
echo "Create provider participant context in IdentityHub"
PEM_PROVIDER=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/provider_public.pem)
DATA_PROVIDER=$(jq -n --arg pem "$PEM_PROVIDER" '{
            "roles":[],
            "serviceEndpoints":[
              {
                 "type": "CredentialService",
                 "serviceEndpoint": "http://provider-ih:7091/api/credentials/v1/participants/ZGlkOndlYjpwcm92aWRlci1paCUzQTcwOTM6Ym9i",
                 "id": "provider-credentialservice-1"
              },
              {
                "type": "ProtocolEndpoint",
                "serviceEndpoint": "http://provider-connector:8192/api/dsp",
                "id": "provider-catalogserver-dsp"
              }
            ],
            "active": true,
            "participantId": "did:web:provider-ih%3A7093:bob",
            "did": "did:web:provider-ih%3A7093:bob",
            "key":{
                "keyId": "did:web:provider-ih%3A7093:bob#key-1",
                "privateKeyAlias": "key-1",
                "publicKeyPem":"\($pem)"
            }
      }')

# the provider runtime will need to have the client_secret in its vault as well, so we store it in a variable
# and use the Secrets API (part of Management API) to insert it.
clientSecret=$(curl -s --location 'http://localhost:7092/api/identity/v1alpha/participants/' \
--header 'Content-Type: application/json' \
--header "x-api-key: $API_KEY" \
--data "$DATA_PROVIDER" | jq -r '.clientSecret')
echo $clientSecret

# add client secret to the provider runtimes
SECRETS_DATA=$(jq -n --arg secret "$clientSecret" \
'{
  "@context" : {
    "edc" : "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type" : "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id" : "did:web:provider-ih%3A7093:bob-sts-client-secret",
  "https://w3id.org/edc/v0.0.1/ns/value": "\($secret)"
}')

curl -sL -X POST http://localhost:8091/api/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"
curl -sL -X POST http://localhost:8191/api/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"
curl -sL -X POST http://localhost:8291/api/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"

###############################################
# SEED ISSUER SERVICE
###############################################

echo
echo
echo "Create dataspace issuer"
PEM_ISSUER=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/issuer_public.pem)
DATA_ISSUER=$(jq -n --arg pem "$PEM_ISSUER" '{
            "roles":["admin"],
            "serviceEndpoints":[
              {
                 "type": "IssuerService",
                 "serviceEndpoint": "http://localhost:10012/api/issuance/v1alpha/participants/ZGlkOndlYjpsb2NhbGhvc3QlM0ExMDEwMA==",
                 "id": "issuer-service-1"
              }
            ],
            "active": true,
            "participantId": "did:web:localhost%3A10100",
            "did": "did:web:localhost%3A10100",
            "key":{
                "keyId": "did:web:localhost%3A10100#key-1",
                "privateKeyAlias": "key-1",
                "keyGeneratorParams":{
                  "algorithm": "EdDSA"
                }
            }
      }')

curl -s --location 'http://localhost:10015/api/identity/v1alpha/participants/' \
--header 'Content-Type: application/json' \
--data "$DATA_ISSUER"

## Seed participant data to the issuer service
#newman run \
#  --folder "Seed Issuer" \
#  --env-var "ISSUER_ADMIN_URL=http://localhost:10013" \
#  --env-var "CONSUMER_ID=did:web:localhost%3A7083" \
#  --env-var "CONSUMER_NAME=MVD Consumer Participant" \
#  --env-var "PROVIDER_ID=did:web:localhost%3A7093" \
#  --env-var "PROVIDER_NAME=MVD Provider Participant" \
#  ./deployment/postman/MVD.postman_collection.json