import json

import requests


def create_asset(asset_id, management_url, default_headers, baseUrl="https://jsonplaceholder.typicode.com/users"):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
                "@id": asset_id,
                "properties": {"name": asset_id, "contenttype": "application/json"},
                "private_properties": {"name": asset_id, "contenttype": "application/json"},
                "dataAddress": {"name": "Test data", "baseUrl": baseUrl, "type": "HttpData"},
            }
        ),
        url=f"{management_url}/v3/assets",
    )


def create_policy(policy_id, management_url, default_headers, permissions=[]):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/", "odrl": "http://www.w3.org/ns/odrl/2/"},
                "@id": policy_id,
                "policy": {
                    "@context": "http://www.w3.org/ns/odrl.jsonld",
                    "@type": "Set",
                    "odrl:permission": permissions,
                    "odrl:prohibition": [],
                    "odrl:obligation": [],
                },
            }
        ),
        url=f"{management_url}/v2/policydefinitions",
    )


def create_contract_definition(contract_definition_id, management_url, asset_id, policy_id, default_headers):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
                "@id": contract_definition_id,
                "accessPolicyId": policy_id,
                "contractPolicyId": policy_id,
                "assetsSelector": [
                    {"operandLeft": "https://w3id.org/edc/v0.0.1/ns/id", "operator": "in", "operandRight": [asset_id]}
                ],
            }
        ),
        url=f"{management_url}/v3/contractdefinitions",
    )


def fetch_catalog(federated_catalog_url):
    return requests.post(f"{federated_catalog_url}/v1alpha/catalog/query")


def negotiate_contract(offer_id, consumer_management_url, provider_protocol_internal, permissions, default_headers):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "ContractRequest",
                "counterPartyAddress": provider_protocol_internal,
                "protocol": "dataspace-protocol-http",
                "policy": {
                    "@context": "http://www.w3.org/ns/odrl.jsonld",
                    "@id": f"{offer_id}",
                    "@type": "Offer",
                    "assigner": "provider",
                    "target": "assetId",
                    "permission": permissions,
                },
            }
        ),
        url=f"{consumer_management_url}/v3/contractnegotiations",
    )


def get_contract_agreement_id(contract_negotiation_id, management_url, default_headers):
    return requests.get(
        headers=default_headers, url=f"{management_url}/v2/contractnegotiations/{contract_negotiation_id}"
    )


def request_consumer_pull_transfer(
    provider_connector_id,
    consumer_connector_management_url,
    consumer_callback_backend_url,
    counter_party_address_internal,
    contract_agreement_id,
    default_headers,
):

    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "connectorId": provider_connector_id,
                "counterPartyAddress": f"{counter_party_address_internal}",
                "contractId": f"{contract_agreement_id}",
                "assetId": "assetId",
                "protocol": "dataspace-protocol-http",
                "transferType": "HttpData-PULL",
                "dataDestination": {
                    "type": "HttpProxy",
                },
                "callbackAddresses": [{"events": ["transfer.process.started"], "uri": consumer_callback_backend_url}],
            }
        ),
        url=f"{consumer_connector_management_url}/v2/transferprocesses",
    )


def get_transfer_state(consumer_management_url, pull_transfer_id):
    return requests.get(f"{consumer_management_url}/v2/transferprocesses/{pull_transfer_id}/state").json()
