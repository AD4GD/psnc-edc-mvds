# Federated Catalog

The Federated Catalog (FC) represents the aggregated catalogs of multiple participants in a dataspace. To achieve that,
the FC employs a set of crawlers, that periodically scrape the dataspace requesting the catalog from each participant in
a list of participants and consolidates them in a local cache or database (if the appropriate extension is used).

Keeping a locally cached version of every participant's catalog makes catalog queries more responsive and robust, and it
can cause a reduction in network load.

The Federated Catalog is based on EDC components for core functionality, specifically those of
the [connector](https://github.com/eclipse-edc/Connector) for extension loading, runtime bootstrap, configuration, API
handling etc., while adding specific functionality using the EDC extensibility mechanism.

## Project
The following project structure is heavily influenced by the EDC initiative project's structure:
- `/core` - reused packages by launchers
- `/extensions` - custom functionality
- `/gradle` - required for the build
- `/launchers` - build targets

## Launchers
There are two launchers:
- **catalog-iam-daps** – Version with OAuth 2.0 inter-connector authentication enabled
- **catalog-iam-mocked** – Version with a mocked inter-connector authentication mechanism

## Build
`./gradlew <launcher> (e.g. launchers:daps:build)`

## APIs
- `/catalog` - used to query federated catalog

## Definitions
- crawler - process that fetches the most recent version of the data catalog from participants
- catalog - available offers for negotiations
- target node - participant's address

## Extensions
- connector-persistence - required for adding a persistence layer for the connector's control plane. Creates required database scheme if it does not exists
- policy-engine - adds policy rules which can be used for the policy creation

