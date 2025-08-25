#!/bin/bash
## Seed identity data to identityhubs
API_KEY="c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="

# add participant "consumer"
echo
echo
echo "Create consumer participant"
PEM_CONSUMER=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/consumer_public.pem)
DATA_CONSUMER=$(jq -n --arg pem "$PEM_CONSUMER" '{
           "roles":[],
           "serviceEndpoints":[
             {
                "type": "CredentialService",
                "serviceEndpoint": "http://consumer-ih:7081/api/presentation/v1/participants/ZGlkOndlYjpsb2NhbGhvc3QlM0E3MDgz",
                "id": "consumer-credentialservice-1"
             },
             {
                "type": "ProtocolEndpoint",
                "serviceEndpoint": "http://consumer-connector:29194/protocol",
                "id": "consumer-dsp"
             }
           ],
           "active": true,
           "participantId": "did:web:consumer-ih%3A7083",
           "did": "did:web:consumer-ih%3A7083",
           "key":{
               "keyId": "did:web:consumer-ih%3A7083#key-1",
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

# add client secret to the consumer runtime
SECRETS_DATA=$(jq -n --arg secret "$clientSecret" \
'{
  "@context" : {
    "edc" : "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type" : "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id" : "did:web:localhost%3A7083-sts-client-secret",
  "https://w3id.org/edc/v0.0.1/ns/value": "\($secret)"
}')

curl -sL -X POST http://localhost:29193/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"

# add participant "provider"
echo
echo
echo "Create provider participant"
PEM_PROVIDER=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/provider_public.pem)
DATA_PROVIDER=$(jq -n --arg pem "$PEM_PROVIDER" '{
            "roles":[],
            "serviceEndpoints":[
              {
                 "type": "CredentialService",
                 "serviceEndpoint": "http://provider-ih:7091/api/presentation/v1/participants/ZGlkOndlYjpsb2NhbGhvc3QlM0E3MDkz",
                 "id": "provider-credentialservice-1"
              },
              {
                "type": "ProtocolEndpoint",
                "serviceEndpoint": "http://provider-connector:19194/protocol",
                "id": "provider-catalogserver-dsp"
              }
            ],
            "active": true,
            "participantId": "did:web:provider-ih%3A7093",
            "did": "did:web:provider-ih%3A7093",
            "key":{
                "keyId": "did:web:provider-ih%3A7093#key-1",
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

# add client secret to the provider runtimes
SECRETS_DATA=$(jq -n --arg secret "$clientSecret" \
'{
  "@context" : {
    "edc" : "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type" : "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id" : "did:web:localhost%3A7093-sts-client-secret",
  "https://w3id.org/edc/v0.0.1/ns/value": "\($secret)"
}')

curl -sL -X POST http://localhost:19193/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"

# add participant "FC"
echo
echo
echo "Create FC participant"
PEM_FC=$(sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' certs/consumer_public.pem)
DATA_FC=$(jq -n --arg pem "$PEM_FC" '{
           "roles":[],
           "serviceEndpoints":[
             {
                "type": "CredentialService",
                "serviceEndpoint": "http://fc-ih:7181/api/presentation/v1/participants/ZGlkOndlYjpsb2NhbGhvc3QlM0E3MDgz",
                "id": "fc-credentialservice-1"
             },
             {
                "type": "ProtocolEndpoint",
                "serviceEndpoint": "http://federated-catalog:8192/api/dsp",
                "id": "fc-dsp"
             }
           ],
           "active": true,
           "participantId": "did:web:fc-ih%3A7183",
           "did": "did:web:fc-ih%3A7183",
           "key":{
               "keyId": "did:web:fc-ih%3A7183#key-1",
               "privateKeyAlias": "key-1",
               "publicKeyPem":"\($pem)"
           }
       }')

# the provider runtime will need to have the client_secret in its vault as well, so we store it in a variable
# and use the Secrets API (part of Management API) to insert it.
clientSecret=$(curl -s --location 'http://localhost:7182/api/identity/v1alpha/participants/' \
--header 'Content-Type: application/json' \
--header "x-api-key: $API_KEY" \
--data "$DATA_PROVIDER" | jq -r '.clientSecret')

# add client secret to the provider runtimes
SECRETS_DATA=$(jq -n --arg secret "$clientSecret" \
'{
  "@context" : {
    "edc" : "https://w3id.org/edc/v0.0.1/ns/"
  },
  "@type" : "https://w3id.org/edc/v0.0.1/ns/Secret",
  "@id" : "did:web:localhost%3A7093-sts-client-secret",
  "https://w3id.org/edc/v0.0.1/ns/value": "\($secret)"
}')

curl -sL -X POST http://localhost:9191/api/management/v3/secrets -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA"