import datetime
import io
import logging
import mimetypes
import os
from typing import List, Optional

import httpx
import magic
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

IP = "0.0.0.0"  # nosec
PORT = 4000  # nosec


class DataAddressProperties(BaseModel):
    type: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/type")
    endpoint: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/endpoint")
    auth_type: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/authType")
    endpoint_type: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/endpointType")
    authorization: str = Field(..., alias="https://w3id.org/edc/v0.0.1/ns/authorization")


class DataAddress(BaseModel):
    properties: DataAddressProperties


class CallbackAddress(BaseModel):
    uri: str
    events: List[str]
    transactional: bool
    auth_key: Optional[str] = Field(None, alias="authKey")
    auth_code_id: Optional[str] = Field(None, alias="authCodeId")


class Payload(BaseModel):
    transfer_process_id: str = Field(..., alias="transferProcessId")
    callback_addresses: List[CallbackAddress] = Field(..., alias="callbackAddresses")
    asset_id: str = Field(..., alias="assetId")
    type: str
    contract_id: str = Field(..., alias="contractId")
    data_address: DataAddress = Field(..., alias="dataAddress")


class TransferProcessStarted(BaseModel):
    id: str
    at: int
    payload: Payload
    type: str


def get_minio_credentials():
    return {
        "endpoint": os.environ.get("MINIO_ENDPOINT"),
        "access_key": os.environ.get("MINIO_ACCESS_KEY"),
        "secret_key": os.environ.get("MINIO_SECRET_KEY"),
        "is_secure": os.environ.get("MINIO_IS_SECURE"),
    }


@app.post("/edr-endpoint/{proxy_path:path}")
@app.post("/edr-endpoint")
async def edr_endpoint(
    request: Request,
    proxy_path: str = "",
):
    logger.info(request)
    logger.info(proxy_path)
    logger.info("Entering edr endpoint")

    proxy_query_params = request.query_params

    logger.info(proxy_query_params)

    # Parse the request body as JSON
    try:
        request_body = await request.json()
        transfer_process = TransferProcessStarted(**request_body)
        logger.info(request_body)
    except Exception as e:
        logger.error("Error parsing request body: %s", str(e))
        raise HTTPException(status_code=422, detail="Invalid request body")

    minio_data = get_minio_credentials()
    logger.info(minio_data)

    minio_client = Minio(
        endpoint=minio_data["endpoint"],
        access_key=minio_data["access_key"],
        secret_key=minio_data["secret_key"],
        secure=minio_data["is_secure"],
    )

    response = await get_asset_from_provider(transfer_process, proxy_path, proxy_query_params)

    asset_id = transfer_process.payload.asset_id

    print("Start uploading...")
    upload_asset_to_storage(minio_client, response, asset_id)

    return JSONResponse(content={"status": "success"}, status_code=200)


async def get_asset_from_provider(request, proxy_path, proxy_query_params):
    properties = request.payload.data_address.properties
    endpoint = properties.endpoint
    authKey = properties.auth_type
    authCode = properties.authorization

    if not endpoint or not authKey or not authCode:
        return JSONResponse(
            content={"error": "Missing or invalid endpoint, authKey or authCode parameters."}, status_code=400
        )

    if proxy_path is not None and proxy_path:
        endpoint = f"{endpoint}/{proxy_path}"

    if proxy_query_params is not None and proxy_query_params and len(proxy_query_params.items()) > 0:
        endpoint = f"{endpoint}?{proxy_query_params}"

    headers = {"Authorization": authCode}
    logger.info(headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers)
        return response


def upload_asset_to_storage(minio_client, response, asset_id):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    _mime = magic.from_buffer(response.content, mime=True)
    _ext = mimetypes.guess_extension(_mime)
    print(_mime, _ext)

    if _ext:
        final_filename = os.path.join("data", f"{asset_id}-{timestamp}{_ext}")
    else:
        final_filename = os.path.join("data", f"{asset_id}-{timestamp}.bin")

    writable_content = io.BytesIO(response.content)

    bucket = "test"
    create_bucket_if_not_exists(minio_client, bucket)

    minio_client.put_object(
        bucket_name=bucket, object_name=final_filename, data=writable_content, length=len(response.content)
    )


def create_bucket_if_not_exists(client, bucket_name):
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as exc:
        print(f"Error occurred: {exc}")


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    uvicorn.run(app, host=IP, port=PORT)
