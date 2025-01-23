# Data Dashboard

Data Dashboard is a modified version of the
EDC Data Dashboard (https://github.com/eclipse-edc/DataDashboard).
It acts as a frontend application of the edc-connector component.

## Project
The data dashboard project is a SPA based on the Angular frontend framework.

## Run locally
`npm start`

## Paths
- `/introduction` or `/`
- `/browse-catalog` - available offers to negotiate
- `/contracts` - negotiated offers
- `/contract-definitions` - created contract definitions
- `/policies` - defined policies
- `/my-assets` - created assets
- `/transfer-history` - transfer history

## Modifications
- Fixed bugs
- Minor UI changes
- Updated `think-it-labs/edc-connector-client` library version
- Added policy rule presets (policies)
- Added static headers (data transfer)
- Added query parameters (data transfer)
- Added more information on entities (baseUrl, etc.)
