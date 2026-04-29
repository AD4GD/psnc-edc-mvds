import json

import requests


def _build_asset_properties(
    asset_name: str,
    asset_id: str,
    content_type: str,
    baseUrl: str,
    version: str,
    additional_metadata: dict,
    proxy: bool,
):
    base_properties = {
        "name": asset_name if asset_name else asset_id,
        "contenttype": content_type,
        "proxyPath": "true" if proxy else "false",
        "proxyQueryParams": "true" if proxy else "false",
        "version": version,
        "baseUrl": baseUrl,
    }

    # Keep metadata fields on top-level properties (not nested under "metadata").
    extra_properties = additional_metadata if isinstance(additional_metadata, dict) else {}

    # Base EDC properties take precedence over metadata on conflicts.
    return {**extra_properties, **base_properties}


def create_asset(
    asset_id: str,
    management_url: str,
    default_headers: dict,
    asset_name: str = "",
    content_type: str = "application/json",
    baseUrl: str = "https://jsonplaceholder.typicode.com/users",
    additional_metadata: dict = {},
    version: str = "1.0",
    context: dict = {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
    proxy: bool = True,
):
    properties = _build_asset_properties(
        asset_name=asset_name if asset_name else asset_id,
        asset_id=asset_id,
        content_type=content_type,
        baseUrl=baseUrl,
        version=version,
        additional_metadata=additional_metadata,
        proxy=proxy,
    )

    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": context,
                "@id": asset_id,
                "properties": properties,
                "private_properties": {
                    "name": asset_name if asset_name else asset_id,
                    "contenttype": content_type,
                    "proxyPath": "true" if proxy else "false",
                    "proxyQueryParams": "true" if proxy else "false",
                    "version": version,
                    "baseUrl": baseUrl,
                },
                "dataAddress": {
                    "name": "Test data",
                    "baseUrl": baseUrl,
                    "type": "HttpData",
                    "contentType": content_type,
                    "proxyPath": "true" if proxy else "false",
                    "proxyQueryParams": "true" if proxy else "false",
                },
            }
        ),
        url=f"{management_url}/v3/assets",
    )


def update_asset(
    asset_id: str,
    management_url: str,
    default_headers: dict,
    asset_name: str,
    content_type: str = "application/json",
    baseUrl: str = "https://jsonplaceholder.typicode.com/users",
    additional_metadata: dict = {},
    context: dict = {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
    proxy: bool = True,
):
    properties = _build_asset_properties(
        asset_name=asset_name,
        asset_id=asset_id,
        content_type=content_type,
        baseUrl=baseUrl,
        version="1.0",
        additional_metadata=additional_metadata,
        proxy=proxy,
    )
    return requests.put(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": context,
                "@id": asset_id,
                "properties": properties,
                "private_properties": properties,
                "dataAddress": {
                    "name": asset_name,
                    "baseUrl": baseUrl,
                    "type": "HttpData",
                    "proxyPath": "true" if proxy else "false",
                    "proxyQueryParams": "true" if proxy else "false",
                },
            }
        ),
        url=f"{management_url}/v3/assets",
    )


def get_asset(asset_id: str, management_url: str, default_headers: dict):
    return requests.get(
        headers=default_headers,
        url=f"{management_url}/v3/assets/{asset_id}",
    )


def delete_asset(
    asset_id: str,
    management_url: str,
    default_headers: dict,
):
    return requests.delete(
        headers=default_headers,
        url=f"{management_url}/v3/assets/{asset_id}",
    )


def create_policy(policy_id: str, management_url: str, default_headers: dict, permissions: list = None):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/", "odrl": "http://www.w3.org/ns/odrl/2/"},
                "@id": policy_id,
                "policy": {
                    "@context": "http://www.w3.org/ns/odrl.jsonld",
                    "@type": "Set",
                    "odrl:permission": [] if permissions is None else permissions,
                    "odrl:prohibition": [],
                    "odrl:obligation": [],
                },
            }
        ),
        url=f"{management_url}/v3/policydefinitions",
    )


def create_contract_definition(contract_definition_id: str, management_url: str, asset_id: str, policy_id: str, default_headers: dict):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
                "@id": contract_definition_id,
                "accessPolicyId": policy_id,
                "contractPolicyId": policy_id,
                "assetsSelector": [{"operandLeft": "https://w3id.org/edc/v0.0.1/ns/id", "operator": "in", "operandRight": [asset_id]}],
            }
        ),
        url=f"{management_url}/v3/contractdefinitions",
    )


def delete_contract_definition(
    contract_definition_id: str,
    management_url: str,
    default_headers: dict,
):
    return requests.delete(
        headers=default_headers,
        url=f"{management_url}/v3/contractdefinitions/{contract_definition_id}",
    )


def fetch_catalog(federated_catalog_url: str, default_headers: dict):
    return requests.post(f"{federated_catalog_url}/v1alpha/catalog/query", headers=default_headers)


def negotiate_contract(
    offer_id: str,
    consumer_management_url: str,
    provider_protocol_internal: str,
    permissions: list,
    default_headers: dict,
    asset_id: str,
    provider_id: str
):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "ContractRequest",
                "counterPartyAddress": provider_protocol_internal,
                "protocol": "dataspace-protocol-http:2025-1",
                "policy": {
                    "@context": "http://www.w3.org/ns/odrl.jsonld",
                    "@id": f"{offer_id}",
                    "@type": "Offer",
                    "assigner": provider_id,
                    "target": {"@id": asset_id},
                    "permission": permissions,
                },
            }
        ),
        url=f"{consumer_management_url}/v3/contractnegotiations",
    )


def get_contract_agreement_id(contract_negotiation_id: str, management_url: str, default_headers: dict):
    return requests.get(headers=default_headers, url=f"{management_url}/v3/contractnegotiations/{contract_negotiation_id}")


def request_consumer_pull_transfer(
    provider_connector_id: str,
    consumer_connector_management_url: str,
    consumer_callback_backend_url: str,
    counter_party_address_internal: str,
    contract_agreement_id: str,
    default_headers: dict,
    asset_id: str = "",
):

    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "connectorId": provider_connector_id,
                "counterPartyAddress": f"{counter_party_address_internal}",
                "contractId": f"{contract_agreement_id}",
                "assetId": asset_id,
                "protocol": "dataspace-protocol-http:2025-1",
                "transferType": "HttpData-PULL",
                "dataDestination": {
                    "type": "HttpProxy",
                },
                "callbackAddresses": [{"events": ["transfer.process.started"], "uri": consumer_callback_backend_url}],
            }
        ),
        url=f"{consumer_connector_management_url}/v3/transferprocesses",
    )


def request_consumer_push_transfer(
    provider_connector_id: str,
    consumer_connector_management_url: str,
    data_destination_endpoint: str,
    counter_party_address_internal: str,
    contract_agreement_id: str,
    default_headers: dict,
    asset_id: str = "",
):
    return requests.post(
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "TransferRequestDto",
                "connectorId": provider_connector_id,
                "connectorAddress": f"{counter_party_address_internal}",
                "contractId": f"{contract_agreement_id}",
                "assetId": asset_id,
                "protocol": "dataspace-protocol-http:2025-1",
                "transferType": "HttpData-PUSH",
                "dataDestination": {"type": "HttpData", "baseUrl": f"{data_destination_endpoint}"},
            }
        ),
        url=f"{consumer_connector_management_url}/v3/transferprocesses",
    )


def get_transfer_state(consumer_management_url: str, pull_transfer_id: str, default_headers: dict):
    return requests.get(f"{consumer_management_url}/v3/transferprocesses/{pull_transfer_id}/state", headers=default_headers).json()


def get_transfer_data_credentials(consumer_management_url: str, pull_transfer_id: str, default_headers: dict):
    return requests.get(
        url=f"{consumer_management_url}/v3/edrs/{pull_transfer_id}/dataaddress",
        headers=default_headers,
    ).json()


def get_data_locally(publicUrl: str, auth):
    headers = {"Authorization": auth}

    return requests.get(
        publicUrl,
        headers=headers,
    )


# Fetch for all the contracts that are in the catalog
def get_contracts(consumer_management_url: str, default_headers: dict = None):
    """
    Get all contracts from the provider.
    """
    return requests.post(
        f"{consumer_management_url}/v3/contractagreements/request",
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "QuerySpec",
                "limit": 1000,
                "offset": 0,
            }
        ),
    )


def get_transfers(consumer_management_url: str, default_headers: dict = None):
    """
    Get all transfers from the provider.
    """
    return requests.post(
        f"{consumer_management_url}/v3/transferprocesses/request",
        headers=default_headers,
        data=json.dumps(
            {
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "limit": 1000,
                "offset": 0,
            }
        ),
    )


def get_transfer(transfer_id: str, consumer_management_url: str, default_headers: dict = None):
    """
    Get a specific transfer by ID.
    """
    return requests.get(
        f"{consumer_management_url}/v3/transferprocesses/{transfer_id}",
        headers=default_headers,
    )


def get_offer_id(fetched_catalog, asset_id) -> str | None:
    """
    Fetch for id of the offer (contract definition) in the catalog
    """

    catalogs_array = []
    if isinstance(fetched_catalog, list):
        catalogs_array = fetched_catalog
    else:
        catalogs_array = [fetched_catalog]

    offer_id = None
    for catalog in catalogs_array:
        dcat_dataset = catalog["dcat:dataset"]
        dataset_array = []
        if isinstance(dcat_dataset, list):
            dataset_array = dcat_dataset
        else:
            dataset_array = [dcat_dataset]

        for asset in dataset_array:
            if asset["@id"] == asset_id:
                policy = asset["odrl:hasPolicy"]
                if isinstance(policy, list):
                    return policy[0]["@id"]
                else:
                    return policy["@id"]
    return offer_id


# Check if there is an existing negotiation for the asset
def check_existing_negotiation(asset_id: str, consumer_management_url: str, default_headers: dict) -> str | None:
    """
    Check if there is an existing negotiation for the asset.
    """
    response = get_contracts(consumer_management_url, default_headers)
    if response.status_code != 200:
        print("Error fetching negotiations:", response.status_code)
        return None
    contracts = response.json()
    for contract in contracts:
        if contract["assetId"] == asset_id:
            return contract["@id"]
    return None


# Check if there is an existing transfer negotiation for the given asset and contract agreement
def check_existing_transfer(
    asset_id: str, contract_id: str, callback_address: str, consumer_management_url: str, default_headers: dict
) -> str | None:
    """
    Check if there is an existing transfer for the asset.
    """
    response = get_transfers(consumer_management_url, default_headers)
    if response.status_code != 200:
        print("Error fetching transfers:", response.status_code)
        return None
    transfers = response.json()
    for transfer in transfers:
        if (
            transfer["assetId"] == asset_id
            and transfer["contractId"] == contract_id
            and "uri" in transfer["callbackAddresses"]
            and transfer["callbackAddresses"]["uri"] == callback_address
        ):
            return transfer["@id"]
    return None
