# Connector

The Connector is a core component of the dataspace.
It acts as a main processing unit during the data exchange processes. It is based on Eclipse Dataspace Components (EDC) https://github.com/eclipse-edc/Connector.

## Project
The following project structure is heavily influenced by the EDC initiative project's structure:
- `/core` - reused packages by launchers
- `/extensions` - custom functionality
- `/gradle` - required for the build
- `/launchers` - build targets

## Connector's structure
Connector is composed from the standard EDC packages for the connector (control plane, data plane, etc.), with included two custom extensions (persistence and policies). Current version of EDC packages is 0.10.1.

## Launchers
There are two launchers:
- daps - version with enabled OAuth 2.0 inter-connectors authentication mechanism
- no-daps - version with mocked inter-connectors authentication

## Build
`./gradlew <launcher> (e.g. launchers:daps:build)`

## APIs
- `/api` - used for utility functions (health check, ...)
- `/management` - used to interact with connector's control plane, manage entities (assets, policies, contract definitions)
- `/protocol`
- `/control`
- `/public` - used for accessing an asset data during the data transfer

## Definitions
- asset - dataspace entity, provides description along with the data
- policy - dataspace entity, which defines set of rules to access an asset's data
- contract definition - dataspace entity
- contract agreement - policy linked to a single or multiple assets
- transfer - the process of sending the negotiated data
- participant - organization participating in the dataspace

## Policy
Specified in ODRL notation. Every policy consists of set of rules. There are three types of rules: permission, obligation, prohibition.

- permission - if we met defined condition, then the rule is met. For example it can be a time condition when we can transfer the data, like a specified time interval 
- prohibition - similar to permission but inversely, if we met the condition, then this rule is not met
- obligation - we should do some specified action first, only then this rule will be met. It's linked to a permission rule as a duty

Rules are checked at the specified scope level: negotiation scope, transfer scope, etc. scopes.

Single policy can be linked to multiple assets. To link a policy with assets need to create a contract definition.

## Extensions
- connector-persistence - required for adding a persistence layer for connector's control plane. Creates required database scheme if it is not exists
- policy-engine - adds policy rules which can be used for the policies creation
