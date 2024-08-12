import datetime
import io
import json
import logging
import mimetypes
import os
from typing import List, Optional

import httpx
import magic
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


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


@app.post("/edr-endpoint")
async def edr_endpoint(request: TransferProcessStarted):
    logger.info(request)
    logger.info("Entering edr endpoint")

    minio_data = get_minio_credentials()
    logger.info(minio_data)

    minio_client = Minio(
        endpoint=minio_data["endpoint"],
        access_key=minio_data["access_key"],
        secret_key=minio_data["secret_key"],
        secure=minio_data["is_secure"],
    )

    properties = request.payload.data_address.properties
    endpoint = properties.endpoint
    authKey = properties.auth_type
    authCode = properties.authorization

    if not endpoint or not authKey or not authCode:
        return JSONResponse(
            content={"error": "Missing or invalid endpoint, authKey or authCode parameters."}, status_code=400
        )

    headers = {"Authorization": authCode}
    logger.info(headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers)

    content_type = response.headers.get("content-type")

    print("Start downloading...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join("data", f"{timestamp}.bin")

    _mime = magic.from_buffer(response.content, mime=True)
    _ext = mimetypes.guess_extension(_mime)
    print(_mime, _ext)

    if _ext:
        final_filename = os.path.join("data", f"{timestamp}{_ext}")
    else:
        final_filename = os.path.join("data", f"{timestamp}.bin")

    writable_content = io.BytesIO(response.content)

    bucket = "test"
    create_bucket_if_not_exists(minio_client, bucket)

    minio_client.put_object(
        bucket_name=bucket, object_name=final_filename, data=writable_content, length=len(response.content)
    )

    return JSONResponse(content={"status": "success"}, status_code=200)


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
    uvicorn.run(app, host="0.0.0.0", port=4000)
