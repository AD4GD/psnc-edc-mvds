#!/bin/bash
set -e

COOKIE_JAR="cookies.txt"
CONNECTION_SCRIPT="check_connection.sh"
# URIs
MASTER_REALM="master"
DAPS_REALM="DAPS"
ORGANIZATIONS_REALM="Organizations"
DAPS_CLIENT_ID="security-admin-console"
RS_CLIENT_ID="data-space"
DAPS_REDIRECT_URI="http://localhost:8081/admin/$MASTER_REALM/console/"
RS_REDIRECT_URI="http://localhost"
REALM_URI="$WEB_HTTP_IDP_URI/admin/realms"
ORGANIZATIONS_USER_URI="$REALM_URI/Organizations/users"
DAPS_CLIENTS_URI="$REALM_URI/DAPS/clients"
# Realms & clients
DAPS_REALM_FILE="daps_realm.json" # daps realm
ORGANIZATIONS_REALM_FILE="organizations_realm.json" # organizations realm
CLIENT_PROVIDER_DAPS_FILE="client_provider_daps.json" # provider
CLIENT_CONSUMER_DAPS_FILE="client_consumer_daps.json" # consumer
CLIENT_FC_DAPS_FILE="client_fc_daps.json" # federated-catalog
# Keys
PROVIDER_KEY="certs/provider-daps.jks"
CONSUMER_KEY="certs/consumer-daps.jks"
FEDERATED_CATALOG_KEY="certs/federated-catalog-daps.jks"
KEY_ALIAS="dapsPrivate"
KEYSTORE_PASSWORD="1234"
KEYSTORE_FORMAT="JKS"

if [ $RUN_SCRIPT -eq 0 ]; then
	echo "=== Skipping script execution ===" > /dev/stderr
	exit 0
fi

function auth_flow() {
	local REALM=$1
	local CLIENT_ID=$2
	local REDIRECT_URI=$3
	local USERNAME=$4
	local PASSWORD=$5

	CODE_VERIFIER=$(head -c 40 /dev/urandom | base64 | tr -d '=+/ ' | cut -c1-128)
	CODE_CHALLENGE=$(echo -n $CODE_VERIFIER | shasum -a 256 | head -c 64 | xxd -r -p | base64 | tr '/+' '_-' | tr -d '=')

	echo "Code_verifier:    $CODE_VERIFIER" > /dev/stderr
	echo "Code_challenge:   $CODE_CHALLENGE" > /dev/stderr

	echo "=== URL to authorization ===" > /dev/stderr
	AUTH_URL="$WEB_HTTP_IDP_URI/realms/$REALM/protocol/openid-connect/auth?client_id=$CLIENT_ID&redirect_uri=$REDIRECT_URI&response_type=code&scope=openid&code_challenge=$CODE_CHALLENGE&code_challenge_method=S256"
	echo "$AUTH_URL" > /dev/stderr

	echo "=== Saving cookies ===" > /dev/stderr
	AUTH_PAGE=$(curl -L -c "$COOKIE_JAR" -s "$AUTH_URL")

	# Etract data from login form
	LOGIN_ACTION=$(echo "$AUTH_PAGE" | sed -n 's/.*action="\([^"]*\)".*/\1/p' | head -n 1 | sed 's/&amp;/\&/g' | sed 's|http://localhost:8081|http://identity-provider:8080|')

	echo "Login action URL:  $LOGIN_ACTION" > /dev/stderr
	echo "=== Sending credentials ===" > /dev/stderr

	RESPONSE=$(curl -b $COOKIE_JAR -c $COOKIE_JAR "$LOGIN_ACTION" \
		-d "username=$USERNAME" \
		-d "password=$PASSWORD" \
		-d "credentialId=" \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-H "Referer: $AUTH_URL" \
		-s -L -i)

	echo "$RESPONSE" > /dev/stderr
	# Extract code from URL
	AUTH_CODE=$(echo "$RESPONSE" | sed -n 's/.*Location:.*code=\([^&]*\).*/\1/p' | tr -d '\r')
	echo "=== Authorization code: $AUTH_CODE ===" > /dev/stderr

	if [[ -z "$AUTH_CODE" ]]; then
		echo "[ERROR] Unable to retrieve authorization code and to login..." > /dev/stderr
		exit 1
	fi

	echo "=== Authorization code: $AUTH_CODE ===" > /dev/stderr
	echo "=== Downloading access_token ===" > /dev/stderr

	TOKEN_RESPONSE=$(curl -s \
		-X POST "$WEB_HTTP_IDP_URI/realms/$REALM/protocol/openid-connect/token" \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "grant_type=authorization_code" \
		-d "code=$AUTH_CODE" \
		-d "client_id=$CLIENT_ID" \
		-d "redirect_uri=$REDIRECT_URI" \
		-d "code_verifier=$CODE_VERIFIER")

	ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

	if [[ "$ACCESS_TOKEN" == "null" || -z "$ACCESS_TOKEN" ]]; then
		echo "[ERROR] Unable to retrieve access token" > /dev/stderr
		exit 1
	fi
	echo "$ACCESS_TOKEN"
}

function post_file() {
	local file=$1
	local uri=$2
	local access_token=$3

	RES=$(curl -S -L \
		-X POST "$uri" \
		-H "Authorization: Bearer $access_token" \
		-H "Content-Type: application/json" \
		-d @"$file" )
	echo $RES > /dev/stderr
}

function request_json() {
	local payload=$1
	local uri=$2
	local access_token=$3
	local method=$4

	RES=$(curl -S -L \
		-X $method "$uri" \
		-H "Authorization: Bearer $access_token" \
		-H "Content-Type: application/json" \
		-d "$payload" )
	echo $RES > /dev/stderr
}

function upload_certificate() {
	local client_id=$1
	local certificate_file=$2
	local access_token=$3

	RES=$(curl -s -L \
		-X POST "$REALM_URI/DAPS/clients/$client_id/certificates/jwt.credential/upload-certificate" \
		-H "Authorization: Bearer $access_token" \
		-H "Content-Type: multipart/form-data" \
		-F "keystoreFormat=$KEYSTORE_FORMAT" \
		-F "keyAlias=$KEY_ALIAS" \
		-F "storePassword=$KEYSTORE_PASSWORD" \
		-F "file=@$certificate_file" )
	echo $RES > /dev/stderr
}

function get_response() {
	local uri=$1
	local access_token=$2

	echo $(curl -S -L \
		-X GET "$uri" \
		-H "Authorization: Bearer $access_token" \
		-H "Content-Type: application/json" )
}

echo "=== Starting idp-filler ==="
echo "=== Waiting for identity-provider to be ready ==="
x=1
while :;
do
	if [[ $(./$CONNECTION_SCRIPT $WEB_HTTP_IDP_URI) == "1" ]]; then
		echo "=== Identity-provider is running ==="
		break
	elif [[ $x -gt 60 ]]; then
		echo "[ERROR] Identity-provider is not running"
		exit 1
	else
		echo "=== Waiting for identity-provider to be ready ==="
		sleep 1
	fi
	x=$(( x + 1 ))
done

IDP_ACCESS_TOKEN=$(auth_flow $MASTER_REALM $DAPS_CLIENT_ID $DAPS_REDIRECT_URI $IDP_USERNAME $IDP_PASSWORD)

echo "=== Adding realms ===" > /dev/stderr
post_file "$DAPS_REALM_FILE" "$REALM_URI" "$IDP_ACCESS_TOKEN"
post_file "$ORGANIZATIONS_REALM_FILE" "$REALM_URI" "$IDP_ACCESS_TOKEN"
echo "=== Adding DAPS clients ===" > /dev/stderr
post_file "$CLIENT_FC_DAPS_FILE" "$DAPS_CLIENTS_URI" "$IDP_ACCESS_TOKEN"

echo "=== Adding Organizations' user ===" > /dev/stderr
USER_PAYLOAD=$(jq -n \
	--arg locale "" \
	--arg email "edc@edc.com" \
	--argjson emailVerified true \
	--argjson enabled true \
	--arg firstName "edc" \
	--arg lastName "edc" \
	--arg username "$RS_USERNAME" \
	--argjson requiredActions [] \
	--argjson groups [] \
	'{
		attributes: { locale: $locale },
		email: $email,
		emailVerified: $emailVerified,
		enabled: $enabled,
		firstName: $firstName,
		lastName: $lastName,
		username: $username,
		requiredActions: $requiredActions,
		groups: $groups
	}')

request_json "$USER_PAYLOAD" "$ORGANIZATIONS_USER_URI" "$IDP_ACCESS_TOKEN" "POST"

USERS_RESPONSE=$(get_response "$REALM_URI/Organizations/ui-ext/brute-force-user" "$IDP_ACCESS_TOKEN")

if [[ -z "$USERS_RESPONSE" || "$USERS_RESPONSE" == "null" ]]; then
	echo "[ERROR] Unable to fetch users or empty response." > /dev/stderr
	exit 1
fi
# ORGANIZATIONS_USERNAME
PSNC_ID=$(echo "$USERS_RESPONSE" | jq -r '.[] | select(.username == "psnc") | .id')

RESET_PASSWORD_PAYLOAD=$(jq -n \
	--arg value "$RS_PASSWORD" \
	--arg temporary false \
	--arg type "password" \
	'{
		value: $value,
		temporary: $temporary,
		type: $type
	}')

request_json "$RESET_PASSWORD_PAYLOAD" "$ORGANIZATIONS_USER_URI/$PSNC_ID/reset-password" "$IDP_ACCESS_TOKEN" "PUT"

# Add to registration service
x=1
while :;
do
	if [[ $(./$CONNECTION_SCRIPT $WEB_HTTP_RS_URI) == "1" ]]; then
		echo "=== Registration service is running ==="
		RS_ACCESS_TOKEN=$(auth_flow $ORGANIZATIONS_REALM $RS_CLIENT_ID $RS_REDIRECT_URI $RS_USERNAME $RS_PASSWORD)

		ADD_PARTICIPANT_RES=$(curl -s -L \
		-X POST "$WEB_HTTP_RS_URI/authority/registry/participants?did=consumer&protocolUrl=http://consumer-connector:29194/protocol" \
		-H "Authorization: Bearer $RS_ACCESS_TOKEN")
		ADD_PARTICIPANT_RES=$(curl -s -L \
		-X POST "$WEB_HTTP_RS_URI/authority/registry/participants?did=provider&protocolUrl=http://provider-connector:19194/protocol" \
		-H "Authorization: Bearer $RS_ACCESS_TOKEN")
		echo "Participants added to registration service" > /dev/stderr
		break
	elif [[ $x -gt 60 ]]; then
		echo "[ERROR] Registration service is not running"
		post_file "$CLIENT_PROVIDER_DAPS_FILE" "$DAPS_CLIENTS_URI" "$IDP_ACCESS_TOKEN"
		post_file "$CLIENT_CONSUMER_DAPS_FILE" "$DAPS_CLIENTS_URI" "$IDP_ACCESS_TOKEN"
		break
	else
		echo "=== Waiting for registration service to be ready ==="
		sleep 1
	fi
	x=$(( x + 1 ))
done
sleep 5 # Wait for the clients to be created

CLIENTS_RESPONSE=$(get_response "$DAPS_CLIENTS_URI" "$IDP_ACCESS_TOKEN")
if [[ -z "$CLIENTS_RESPONSE" || "$CLIENTS_RESPONSE" == "null" ]]; then
	echo "[ERROR] Unable to fetch clients or empty response." > /dev/stderr
	exit 1
fi

# Select the client IDs for consumer, provider, and federated-catalog
PROVIDER_ID=$(echo "$CLIENTS_RESPONSE" | jq -r '.[] | select(.clientId == "provider") | .id')
CONSUMER_ID=$(echo "$CLIENTS_RESPONSE" | jq -r '.[] | select(.clientId == "consumer") | .id')
FEDERATED_CATALOG_ID=$(echo "$CLIENTS_RESPONSE" | jq -r '.[] | select(.clientId == "federated-catalog") | .id')

echo "=== Uploading certificates to clients ===" > /dev/stderr
upload_certificate "$PROVIDER_ID" "$PROVIDER_KEY" "$IDP_ACCESS_TOKEN"
upload_certificate "$CONSUMER_ID" "$CONSUMER_KEY" "$IDP_ACCESS_TOKEN"
upload_certificate "$FEDERATED_CATALOG_ID" "$FEDERATED_CATALOG_KEY" "$IDP_ACCESS_TOKEN"
