# Registration Service

Service created for handling register flow of new participants (companies / nodes with connectors) and users. This service supports [Decentralized Claims Protocol](https://projects.eclipse.org/proposals/eclipse-dataspace-decentralized-claims-protocol) (DCP) which defines an interoperable overlay to the [Dataspace Protocol](https://docs.internationaldataspaces.org/ids-knowledgebase/dataspace-protocol) (DSP) Specifications for conveying organizational identities and establishing trust in a way that preserves privacy and limits the possibility of network disruption. \
This registratiorn service is a part of Data Space Portal developed by [PCSS](https://www.pcss.pl/).

## Principles

We emphasize data protection and isolation, effective action, and minimalism in operations. That's why we use DCP - it secures data, digital currency of modern world, and allows participants to keep control of their users.

## Scripts

Install dependencies: \
`make install-dependencies` \
Make sure to have installed `python3` & `pip` (venv is recommended), `make`.

Run in production: \
`make prod`

Migrate db with custom message: \
`make db-migrate`

All available scripts are described in [Makefile](Makefile)

## Flow

#### Participant

#### User
