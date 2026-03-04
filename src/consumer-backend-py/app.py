import datetime
import io
import logging
import mimetypes
import os
import posixpath
from typing import List, Optional

import boto3
import httpx
import magic
import uvicorn
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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


def get_storage_credentials():
    return {
        "endpoint": os.environ.get("STORAGE_ENDPOINT"),
        "access_key": os.environ.get("STORAGE_ACCESS_KEY"),
        "secret_key": os.environ.get("STORAGE_SECRET_KEY"),
        "is_secure": os.environ.get("STORAGE_IS_SECURE"),
    }


def _env_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def get_s3_config():
    endpoint_url = os.environ.get("S3_ENDPOINT_URL")

    # Backward-compatible: accept STORAGE_ENDPOINT with or without scheme.
    if not endpoint_url:
        storage_data = get_storage_credentials()
        endpoint = (storage_data.get("endpoint") or "").strip() if storage_data else ""
        is_secure = _env_bool(storage_data.get("is_secure"), default=False)
        if endpoint:
            if endpoint.startswith("http://") or endpoint.startswith("https://"):
                endpoint_url = endpoint
            else:
                scheme = "https" if is_secure else "http"
                endpoint_url = f"{scheme}://{endpoint}"

    access_key = os.environ.get("S3_ACCESS_KEY") or os.environ.get("STORAGE_ACCESS_KEY")
    secret_key = os.environ.get("S3_SECRET_KEY") or os.environ.get("STORAGE_SECRET_KEY")

    bucket = os.environ.get("S3_BUCKET") or os.environ.get("STORAGE_BUCKET") or "test"
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("S3_REGION") or "us-east-1"
    prefix = os.environ.get("S3_PREFIX") or "data"

    return {
        "endpoint_url": endpoint_url,
        "access_key": access_key,
        "secret_key": secret_key,
        "bucket": bucket,
        "region": region,
        "prefix": prefix,
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

    s3_config = get_s3_config()
    logger.info({k: ("***" if "key" in k else v) for k, v in s3_config.items()})
    if not s3_config["endpoint_url"]:
        raise HTTPException(status_code=500, detail="S3 endpoint is not configured (S3_ENDPOINT_URL or STORAGE_ENDPOINT)")
    if not s3_config["access_key"] or not s3_config["secret_key"]:
        raise HTTPException(status_code=500, detail="S3 credentials are not configured (S3_ACCESS_KEY/S3_SECRET_KEY or STORAGE_ACCESS_KEY/STORAGE_SECRET_KEY)")

    s3_client = boto3.client(
        "s3",
        endpoint_url=s3_config["endpoint_url"],
        aws_access_key_id=s3_config["access_key"],
        aws_secret_access_key=s3_config["secret_key"],
        region_name=s3_config["region"],
        config=Config(signature_version="s3v4"),
    )

    response = await get_asset_from_provider(transfer_process, proxy_path, proxy_query_params)

    asset_id = transfer_process.payload.asset_id

    print("Start uploading...")
    upload_asset_to_storage(s3_client, s3_config, response, asset_id)

    return JSONResponse(content={"status": "success"}, status_code=200)


async def get_asset_from_provider(request, proxy_path, proxy_query_params):
    properties = request.payload.data_address.properties
    endpoint = properties.endpoint
    authKey = properties.auth_type
    authCode = properties.authorization

    if not endpoint or not authKey or not authCode:
        return JSONResponse(content={"error": "Missing or invalid endpoint, authKey or authCode parameters."}, status_code=400)

    if proxy_path is not None and proxy_path:
        endpoint = f"{endpoint}/{proxy_path}"

    if proxy_query_params is not None and proxy_query_params and len(proxy_query_params.items()) > 0:
        endpoint = f"{endpoint}?{proxy_query_params}"

    headers = {"Authorization": authCode}
    logger.info(headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers)
        return response


def upload_asset_to_storage(s3_client, s3_config, response, asset_id):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    _mime = magic.from_buffer(response.content, mime=True)
    _ext = mimetypes.guess_extension(_mime)
    print(_mime, _ext)

    prefix = (s3_config.get("prefix") or "data").strip("/")
    filename = f"{asset_id}-{timestamp}{_ext}" if _ext else f"{asset_id}-{timestamp}.bin"
    object_key = posixpath.join(prefix, filename)

    writable_content = io.BytesIO(response.content)

    bucket = s3_config["bucket"]
    ensure_bucket_exists(s3_client, bucket)

    content_type = response.headers.get("content-type") or _mime
    s3_client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=writable_content.getvalue(),
        ContentType=content_type,
    )


def ensure_bucket_exists(client, bucket_name: str) -> None:
    try:
        client.head_bucket(Bucket=bucket_name)
        return
    except ClientError as exc:
        error_code = (exc.response.get("Error") or {}).get("Code")
        if error_code not in {"404", "NoSuchBucket", "NotFound"}:
            raise

    try:
        client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as exc:
        error_code = (exc.response.get("Error") or {}).get("Code")
        if error_code in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
            return
        raise


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    uvicorn.run(app, host=IP, port=PORT)
