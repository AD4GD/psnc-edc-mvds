#!/bin/bash
set -e

function log() {
	echo "$(date +'%Y-%m-%d %H:%M:%S') $1"
}

log "=== RUNNING INTEGRATION TESTS ==="
# URLs
LOCALHOST="http://localhost"
PROVIDER_API="http://provider-connector:19191/api"
PROVIDER_MANAGEMENT="http://provider-connector:19193/management"
CONSUMER_API="http://consumer-connector:29191/api"
CONSUMER_MANAGEMENT="http://consumer-connector:29193/management"
FEDERATED_CATALOG_URL="http://federated-catalog:8181/catalog"
MINIO_ADDRESS="http://minio:9001/minio/webrpc"
CONSUMER_BACKEND_EDR="http://consumer-backend:4000/edr-endpoint"
PROVIDER_PROTOCOL_INTERNAL="http://provider-connector:19194/protocol"
# PROVIDER_API="$LOCALHOST:19191/api"
# PROVIDER_MANAGEMENT="$LOCALHOST:19193/management"
# CONSUMER_API="$LOCALHOST:29191/api"
# CONSUMER_MANAGEMENT="$LOCALHOST:29193/management"
# FEDERATED_CATALOG_URL="$LOCALHOST:9181/catalog"
# MINIO_ADDRESS="$LOCALHOST:9001/minio/webrpc"
# DATA_SOURCE_PORT="5000"
# MINIO_ACCESS_KEY="minio-user"
# MINIO_SECRET_KEY="minio-password"

# Default headers
HEADERS="-H x-api-key:edc -H Content-Type:application/json"
RETURN_CODE='--write-out %{http_code}\n -o /dev/null'
RETURN_SIZE='--write-out %{size_download}\n -o /dev/null'

# IDs
# UUID=$(cat /proc/sys/kernel/random/uuid)
UUID=$(uuidgen)
ASSET_ID="asset-$UUID"
POLICY_ID="policy-$UUID"
CONTRACT_DEF_ID="contract-definition-$UUID"
# ASSET_ID="test-asset"
# POLICY_ID="test-policy"
# CONTRACT_DEF_ID="test-contract-definition"

urls_to_download=("formats/csv" "formats/text" "formats/html" "formats/binary" "formats/file" "formats/stream")

log "=== Waiting for idp-filler to finish ==="
idp_x=0
while :;
do
	if [[ $idp-x -gt 60 ]]; then
		log "[ERROR] idp-filler is failing"
		break
	fi
	{ ping idp-filler -c 1;
	res=$?
	if [[ res -ne 0 ]]; then
		break 
	else
		sleep 1
	fi } || { log "idp-filler finished job"; break; }
	idp_x=$(( idp_x + 1 ))
done

# 1. Conn Check
log "=== Conn Check ==="
x=1
while :;
do
	if [[ $(curl -s -X GET $HEADERS $RETURN_CODE "${PROVIDER_API}/check/health/") -eq 200 && $(curl -s -X GET $HEADERS $RETURN_CODE "${CONSUMER_API}/check/health/") -eq 200 ]]; then
		log "=== Provider API is running ==="
		log "=== Consumer API is running ==="
		break
	elif [[ $x -gt 60 ]]; then
		log "[ERROR] Provider is not running"
		log "[ERROR] Consumer is not running"
		exit 1
	else
		log "=== Waiting for providers to be ready ==="
		sleep 1
	fi
	x=$(( x + 1 ))
done

# 2. Asset upload
log "=== Add asset ==="
ASSET_PAYLOAD=$(jq -n \
	--arg id "$ASSET_ID" \
	--arg properties_name "$ASSET_ID" \
	--arg properties_contenttype "application/json" \
	--arg baseUrl "http://data-source:$DATA_SOURCE_PORT" \
	'{
		"@context" : { "edc" : "https://w3id.org/edc/v0.0.1/ns/" },
		"@id" : $id,
		"properties" : {
			"name" : $properties_name,
			"contenttype" : $properties_contenttype,
			"proxyPath" : "true",
			"proxyQueryParams" : "true",
			"metadata" : { },
			"baseUrl" : $baseUrl
		},
		"private_properties" : {
			"name" : $properties_name,
			"contenttype" : $properties_contenttype,
			"proxyPath" : "true",
			"proxyQueryParams" : "true",
			"metadata" : { },
			"baseUrl" : $baseUrl
		},
		"dataAddress" : {
			"type" : "HttpData",
			"name" : $id,
			"proxyPath" : "true",
			"proxyQueryParams" : "true",
			"baseUrl" : $baseUrl
		},
	}')
ASSET_RES=$(curl -s -X POST $RETURN_CODE $HEADERS "$PROVIDER_MANAGEMENT/v3/assets" -d "$ASSET_PAYLOAD")

if [[ $ASSET_RES -eq 200 ]] || [[ $ASSET_RES -eq 409 ]] ; then
	log "=== Asset added successfully ==="
	log $ASSET_RES
else
	log "[ERROR] Unable to add asset! Response code: $ASSET_RES"
	exit 1
fi

# 3. Policy addition
log "=== Add policy ==="
POLICY_PAYLOAD=$(jq -n \
	--arg id "$POLICY_ID" \
	'{
		"@context": {
			"edc" : "https://w3id.org/edc/v0.0.1/ns/",
			"odrl" : "http://www.w3.org/ns/odrl/2/",
		},
		"@id" : $id,
		"policy" : {
			"@context" : "http://www.w3.org/ns/odrl.jsonld",
			"@type" : "Set",
			"odrl:permission": [],
			"odrl:prohibition": [],
			"odrl:obligation": [],
		},
	}')
POLICY_RES=$(curl -s -X POST $RETURN_CODE $HEADERS "${PROVIDER_MANAGEMENT}/v2/policydefinitions" -d "$POLICY_PAYLOAD")
if [[ $POLICY_RES -eq 200 ]] || [[ $POLICY_RES -eq 409 ]] ; then
	log "=== Policy added successfully ==="
	log $POLICY_RES
else
	log "[ERROR] Unable to add asset! Response code: $POLICY_RES"
	exit 1
fi

# 4. Contract definition addition
log "=== Add contract definition ==="
CONTRACT_DEF_PAYLOAD=$(jq -n \
	--arg cdef_id "$CONTRACT_DEF_ID" \
	--arg policy_id "$POLICY_ID" \
	--arg asset_id "$ASSET_ID" \
	--arg edc_context "https://w3id.org/edc/v0.0.1/ns/" \
	--arg operandLeft "https://w3id.org/edc/v0.0.1/ns/id" \
	'{
		"@context" : { "edc" : "https://w3id.org/edc/v0.0.1/ns/" },
		"@id" : $cdef_id,
		"accessPolicyId" : $policy_id,
		"contractPolicyId" : $policy_id,
		"assetsSelector" : [
			{
				"operandLeft" : "https://w3id.org/edc/v0.0.1/ns/id",
				"operator": "in",
				"operandRight": [$asset_id]
			}
		],
	}')
CDEF_RES=$(curl -s -X POST $RETURN_CODE $HEADERS "$PROVIDER_MANAGEMENT/v2/contractdefinitions" -d "$CONTRACT_DEF_PAYLOAD")
if [[ $CDEF_RES -eq 200 ]] || [[ $CDEF_RES -eq 409 ]] ; then
	log "=== Contract definition added successfully ==="
	log $CDEF_RES
else
	log "[ERROR] Unable to add asset! Response code: $CDEF_RES"
	exit 1
fi

# Wait for catalog to update
log "=== Waiting for catalog to update ==="
sleep 60

# 5. Pobranie katalogu
log "=== Fetch catalog ==="
CATALOG=$(curl -sL -X POST $HEADERS "$FEDERATED_CATALOG_URL/v1alpha/catalog/query")
if [ ${#CATALOG[@]} -eq 0 ]; then
    log "Error: Catalog is empty!"
	exit 1
fi

log $CATALOG

# Extract offer_id for given asset_id
OFFER_ID=$(printf '%s' "$CATALOG" | jq -r --arg asset_id "$ASSET_ID" '
  .[]
  | select(."@type" == "dcat:Catalog")
  | .["dcat:dataset"] as $ds
  | ($ds | type) as $dstype
  | if $dstype == "array" then $ds[]? else $ds end
  | select(.id == $asset_id)
  | ."odrl:hasPolicy"."@id"
')

if [[ -z "$OFFER_ID" ]]; then
	log "[ERROR] Unable to retrieve offer ID!"
	exit 1
else
	log "Offer: $OFFER_ID"
fi

# 7. Contract negotiation
log "=== Negotiate contract ==="
NEGOTIATION_PAYLOAD=$(jq -n \
	--arg offer_id "$OFFER_ID" \
	--arg provider_protocol_internal "$PROVIDER_PROTOCOL_INTERNAL" \
	--argjson permissions [] \
'{
	"@context": { "edc" : "https://w3id.org/edc/v0.0.1/ns/" },
	"@type" : "ContractRequest",
	"counterPartyAddress" : $provider_protocol_internal,
	"protocol" : "dataspace-protocol-http",
	"policy" : {
		"@context" : "http://www.w3.org/ns/odrl.jsonld",
		"@id" : $offer_id,
		"@type" : "Offer",
		"assigner" : "provider",
		"target" : "assetId",
		"permission" : $permissions,
	},
}')
NEGOTIATION=$(curl -s -X POST $HEADERS "${CONSUMER_MANAGEMENT}/v3/contractnegotiations" -d "$NEGOTIATION_PAYLOAD")
NEGOTIATION_ID=$(echo "$NEGOTIATION" | jq -r '.["@id"]')

if [[ -z "$NEGOTIATION_ID" ]]; then
	log "[ERROR] Unable to retrieve negotiation ID!"
	exit 1
else
	log "NegotiationId: $NEGOTIATION_ID"
fi

log "=== Waiting for contract agreement ==="
for i in {1..30}; do
	AGREEMENT=$(curl -s $HEADERS "$CONSUMER_MANAGEMENT/v2/contractnegotiations/$NEGOTIATION_ID")
	AGREEMENT_ID=$(echo "$AGREEMENT" | jq -r '.contractAgreementId // empty')
	if [[ -n "$AGREEMENT_ID" ]]; then
		log "AgreementId: $AGREEMENT_ID"
		break
	fi
	sleep 1
done

if [[ -z "$AGREEMENT_ID" ]]; then
	log "Błąd: nie uzyskano contractAgreementId!"
	exit 1
fi

# 9. Get MinIO credentials
log "=== Get MinIO credentials ==="
MINIO_LOGIN_PAYLOAD=$(jq -n \
	--arg minio_user $MINIO_ACCESS_KEY \
	--arg minio_password $MINIO_SECRET_KEY \
	'{
		"id": 1,
		"jsonrpc": "2.0",
		"method": "Web.Login",
		"params": {
			"username": $minio_user,
			"password": $minio_password
		}
	}')
MINIO_CREDENTIALS=$(curl -s \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  $MINIO_ADDRESS -d "$MINIO_LOGIN_PAYLOAD")
MINIO_TOKEN=$(echo $MINIO_CREDENTIALS | jq -r '.result.token')
log "MINIO-TOKEN: $MINIO_TOKEN"

# 10. Transfer asset
log "=== Transfer asset ==="
for url in "${urls_to_download[@]}"; do
	TRANSFER_PAYLOAD=$(jq -n \
		--arg contract_agreement_id "$AGREEMENT_ID" \
		--arg counter_party_address_internal "$PROVIDER_PROTOCOL_INTERNAL" \
		--arg provider_connector_id "provider" \
		--arg CONSUMER_BACKEND_EDR "$CONSUMER_BACKEND_EDR/$url" \
		--arg asset_id "$ASSET_ID" \
	'{
		"@context" : { "@vocab" : "https://w3id.org/edc/v0.0.1/ns/" },
		"connectorId" : $provider_connector_id,
		"counterPartyAddress" : $counter_party_address_internal,
		"contractId" : $contract_agreement_id,
		"assetId" : $asset_id,
		"protocol" : "dataspace-protocol-http",
		"transferType" : "HttpData-PULL",
		"dataDestination" : {
			"type" : "minio",
		},
		"callbackAddresses": [{ "events" : ["transfer.process.started"], "uri" : $CONSUMER_BACKEND_EDR }],
	}')
		
	TRANSFER_RES=$(curl -s -X POST $HEADERS "${CONSUMER_MANAGEMENT}/v3/transferprocesses" -d "$TRANSFER_PAYLOAD")
	TRANSFER_ID=$(echo "$TRANSFER_RES" | jq -r '.["@id"]')
	if [[ -z $TRANSFER_ID ]] ; then
		log "[ERROR] Unable to retrieve transfer ID!"
		exit 1
	else
		log "TransferID: $TRANSFER_ID"
	fi

	y=1
	while :;
	do
		TRANSFER_STATUS=$(curl -s $HEADERS "${CONSUMER_MANAGEMENT}/v3/transferprocesses/$TRANSFER_ID")
		STATE=$(echo "$TRANSFER_STATUS" | jq -r '.state')
		if [[ $y -gt 30 ]]; then
			log "[ERROR] Could not start transfer process"
			exit 1
		elif [[ $STATE == "STARTED" ]]; then
			break
		else
			y=$(( y + 1 ))
			sleep 1
			continue
		fi
	done
	
	RES=$(curl -s $HEADERS $RETURN_CODE "${CONSUMER_MANAGEMENT}/v3/transferprocesses/$TRANSFER_ID")
	if [[ $RES -eq 200 ]]; then
		log "=== Successfully downloaded $url ==="
	else
		log "[ERROR] Failed to download $url! Response code: $RES"
		exit 1
	fi
done

MINIO_BUCKET_NAME=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Authorization: Bearer $MINIO_TOKEN" \
  $MINIO_ADDRESS -d '{
  	"id": 1,
	"jsonrpc": "2.0",
	"params": { },
	"method": "Web.ListBuckets"
  }' | jq -r '.result.buckets[0].name')
echo "MINIO-BUCKET-NAME: $MINIO_BUCKET_NAME"

MINIO_BUCKET_PAYLOAD=$(jq -n \
	--arg bucket_name $MINIO_BUCKET_NAME \
	'{
		"id": 1,
		"jsonrpc": "2.0",
		"method": "Web.ListObjects",
		"params": {
			"bucketName": $bucket_name,
			"prefix": "data/"
		}
	}')

MINIO_ITEMS=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Authorization: Bearer $MINIO_TOKEN" \
  $MINIO_ADDRESS -d "$MINIO_BUCKET_PAYLOAD" | jq -r '.result.objects')

MINIO_SIZES=($(echo "$MINIO_ITEMS" | jq '.[] | .size' | awk '{printf "%s ", $1}'))

for index_url in "${!urls_to_download[@]}"; do
	DS_SIZE=$(curl -s $RETURN_SIZE "$LOCALHOST:$DATA_SOURCE_PORT/${urls_to_download[$index_url]}")
	if [[ $DS_SIZE -ne ${MINIO_SIZES[$index_url]} ]]; then
		log "[ERROR] Invalid size for ${MINIO_SIZES[$index_url]}: ${MINIO_SIZES[$index_url]} vs $DS_SIZE"
		exit 1
	else
		log "Valid size for ${MINIO_SIZES[$index_url]}: $DS_SIZE"
	fi	
done

log "=== All tests finished successfully ==="
