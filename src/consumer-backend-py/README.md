# Consumer backend

Consumer backend is a service responsible for getting and saving the asset data in _consumer pull_ data transfer scenario.

## Endpoints
- `/edr-endpoint` is a POST endpoint, called automatically as a callback during the data transfer in case of _consumer pull_.

## Motivation
Since we are using _consumer pull_ scenario only, while transferring the data, we need some service which will be called as a callback then it will get the data ready for transfer and save it into designated data source, currently it is Minio object storage.

Potentially we can use _consumer push_ scenario, in that case this component can be refactored to act as a CRUD API for the data sink.