

# AD4GD Demo connector

This repo contains an Eclipse Dataspace Components (EDC) Connector for the use-case in the AD4GD context.

The connector configuration is based on the EDC Samples and the sovity EDC. The main features are:
- persistence for assests, policies, contracts etc
- data transfer via HTTP pull method  

**Note:** _Currently, there is only a noop implementation of the data encryptor for the endpoint data reference (EDR) sent to the consumer. Without a proper data encryptor, the actual data address is passed to the consumer. This also affect sensitive data in the data address, although sensitive data should not be stored in the data address._

## Known issues and next steps

There are a couple of things to be done before this setup can be run in a productive enviornment:

critical things:
- authentication of management API -> use https://github.com/eclipse-edc/Connector/tree/main/extensions/common/auth/auth-tokenbased (edc-auth-tokenbased = { module = "org.eclipse.edc:auth-tokenbased", version.ref = "edc" })
- authentication of connectors -> use DAPS or webdid. For DAPS consider the following repos:
    - DAPS implementation: https://github.com/International-Data-Spaces-Association/omejdn-daps (https://github.com/Fraunhofer-AISEC/omejdn-server)
    - DAPS extension: https://github.com/eclipse-tractusx/daps-registration-service
    - Extention for the connector: https://github.com/eclipse-edc/Connector/tree/a93a66c0e99a215c049cc750483987095df29e30/extensions/common/iam/oauth2/oauth2-core
- encryption of EDR messages in pull methods -> use https://github.com/eclipse-tractusx/tractusx-edc/tree/main/edc-extensions/data-encryption
- binary files (e.g. images) are modified during transfer using the http data plane. See: https://github.com/eclipse-edc/Connector/discussions/2360
- bring the demo into the cloud 


nice to have:
- GUI, with user login
- broker to find data offerings / participants
- extension that populates the connector based on available data in backend systems, like rasdaman or FROST-server


next steps:
- Define/list data formats that are supposed to be shared via connectors (The data shared will influence the requirements of the connector)
- Define how assets are created in the connector for the pilots (Does the consumer needs to be able to set query parameter?)
- Define/investigate how to integrate the connector with the ecosystem on both sides (provider and consumer)
- Define/investigate how to connectors and other project compoents play together




## Build instructions

All commands are executed from the root of the project.

````
./gradlew launcher:build
````


## Run connector

1. Build the connector jar file (see above).

2. Change the ``launcher/config/configuration.properties`` file to your needs. Adjust the port mapping in the ``docker-compose.yaml`` to your changes.

3. Build the docker image and start the connector stack (stack includes connector + postgresSql)

````
./docker compose up --build
````
