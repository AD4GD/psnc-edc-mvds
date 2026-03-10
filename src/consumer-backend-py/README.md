# Consumer Backend

EDC (Eclipse Dataspace Connector) Consumer Backend service - handles data transfer callbacks and storage operations for EDC data transfers.

## Overview

The Consumer Backend is a FastAPI-based microservice that:

1. **Receives transfer process notifications** from the EDC Connector via callback mechanism
2. **Fetches data** from the provider's endpoint using authorization codes
3. **Stores datasets** to S3-compatible object storage (Blob Storage, RustFS, AWS S3, etc.)
4. **Organizes files** by requester participant folders with timestamps

## How It Works

### Architecture Flow

```
EDC Connector (Data Transfer)
        ↓
   [Callback Event]
        ↓
Consumer Backend (/edr-endpoint)
        ↓
   [Fetch Data from Provider]
        ↓
   [Upload to S3 Storage]
```

### Data Transfer Process

1. **Transfer Initiated**: User initiates a transfer from the Data Dashboard
2. **Callback Registration**: Data Dashboard specifies callback URL pointing to Consumer Backend
3. **Transfer Complete**: EDC Connector notifies Consumer Backend at callback URL with transfer details
4. **Data Retrieval**: Consumer Backend fetches data from provider using EDR (Endpoint Data Reference)
5. **Storage Upload**: Data is uploaded to configured S3 storage with proper file type detection

## Usage

### Via Data Dashboard (UI)

1. Open Data Dashboard in your browser
2. Browse catalogs from different connectors
3. Negotiate contracts for desired datasets
4. Initiate transfers and select **storage** as destination
5. Transfer automatically processes through Consumer Backend
6. Files appear in configured storage with correct extensions

### Via Jupyter Notebook

Use the included `example-usage.ipynb` notebook to:
- Trigger transfers programmatically
- Monitor transfer status
- Query available datasets
- Manage storage uploads

See [example-usage.ipynb](./example-usage.ipynb) for detailed examples.

## Endpoints

### POST /edr-endpoint
Main endpoint that receives transfer process notifications.

**Path**: `/edr-endpoint` or `/edr-endpoint/{proxy_path}`

**Purpose**: Handles EDC transfer completion callbacks and manages data retrieval to storage.

### Request Format

Typical callback payload from EDC Connector:

```json
{
  "id": "transfer-process-12345",
  "at": 1709592000,
  "type": "TransferProcessStarted",
  "payload": {
    "transferProcessId": "transfer-process-12345",
    "assetId": "data-asset-001",
    "contractId": "contract-agreement-999",
    "type": "HttpData-PULL",
    "callbackAddresses": [
      {
        "uri": "http://consumer-backend:4000/edr-endpoint?requester=consumer",
        "events": ["transfer.process.started"],
        "transactional": false
      }
    ],
    "dataAddress": {
      "properties": {
        "https://w3id.org/edc/v0.0.1/ns/type": "HttpData",
        "https://w3id.org/edc/v0.0.1/ns/endpoint": "http://provider-connector:19194/public/data/file.json",
        "https://w3id.org/edc/v0.0.1/ns/authType": "bearer",
        "https://w3id.org/edc/v0.0.1/ns/endpointType": "HttpData",
        "https://w3id.org/edc/v0.0.1/ns/authorization": "Bearer eyJhbGc..."
      }
    }
  }
}
```

### Query Parameters

- `requester` - Participant ID initiating the transfer (used for folder organization)
- `requesterParticipant` - Alternative name for requester
- `requestedBy` - Alternative name for requester
- `participant` - Alternative name for requester
- `folder` - Override storage folder name

**Example**: `http://consumer-backend:4000/edr-endpoint?requester=consumer&folder=mycustomer`

### Callback URI Format

When registering transfers via Data Dashboard or API, use:

```
http://consumer-backend:4000/edr-endpoint?requester={connectorId}
```

Where `{connectorId}` is configured in `dashboard configuration` (e.g., "consumer", "provider").

## Configuration

### Environment Variables

```bash
# S3 Storage Configuration
S3_DEFAULT_PREFIX=http://storage:9000
S3_ACCESS_KEY=rustfs-admin
S3_SECRET_KEY=rustfs
S3_BUCKET=downloads
S3_DEFAULT_PREFIX=edc-transfers
S3_DEFAULT_FOLDER=anonymous
```

### File Organization in Storage

Files are organized as:

```
s3://bucket/
  └── [prefix]/
      └── [requester_participant]/
          ├── asset_id-20260305120000.json
          ├── asset_id-20260305120015.csv
          └── asset_id-20260305120030.pdf
```

Example: `s3://downloads/edc-transfers/consumer/data-asset-001-20260305120000.json`

## File Type Handling

The service intelligently determines file extensions:

1. **Priority 1**: Content-Type header from provider response
   - Example: `Content-Type: application/json` → `.json`
   - Skipped if header is `application/octet-stream` (ambiguous)
   
2. **Priority 2**: Magic bytes file type detection from content
   - Analyzes file content structure to identify format
   - Detects common formats: JSON, CSV, PDF, Images, etc.
   
3. **Priority 3**: Fallback to `.json` for unknown types
   - Used when no Content-Type and magic bytes detection fails

Supported MIME types:
- `application/json` → `.json`
- `text/csv` → `.csv`
- `application/pdf` → `.pdf`
- `text/plain` → `.txt`
- `image/png` → `.png`
- `image/jpeg` → `.jpg`
- `application/octet-stream` → `.bin`

## Running

### Local Development

It is a part of ``` docker compose ``` project and it has to be started this way so that connector has access to it via ``` docker network ```

## Logs

Access detailed logs for debugging:

```bash
# Docker
docker logs psnc-edc-mvds-consumer-backend

# Local (with timestamp, request details, data type detection)
[INFO] Consumer Backend - Fetching asset from provider: http://provider-connector:19194/public/data/file.json
[INFO] Response status: 200, Content-Type: application/json
[INFO] Content-Type: application/json, Extension: .json
[INFO] Uploading to S3: bucket=downloads, key=consumer/asset_id-20260305120000.json
[INFO] Successfully uploaded asset_id-20260305120000.json to S3
```

## Error Handling

The service provides clear error responses:

- **400 Bad Request**: Missing/invalid callback payload or endpoint data
- **500 Internal Error**: S3 configuration or storage upload issues

Example error:
```json
{
  "error": "Missing or invalid endpoint, authType or authorization parameters."
}
```

## Troubleshooting

### Files saved as .bin instead of correct extension

**Cause**: No Content-Type header from provider AND magic bytes detection failed

**Solution**: 
- Ensure provider includes `Content-Type` header in response
- If provider sends binary data without proper Content-Type, magic bytes detection may fail
- Service defaults to `.json` for undetected types (not `.bin`)

### Transfer callback not reaching backend

**Check**:
- Callback URL has correct IP/hostname (localhost vs docker service name)
- Port 4000 is exposed and accessible
- Firewall rules allow callback traffic
- `requester` query parameter must match `connectorId` in config

### S3 upload fails

**Check**:
- S3 endpoint URL is accessible from backend container
- Access keys are correct
- Bucket exists and is writable
- IAM permissions allow PutObject operations

## Integration Points

### Data Dashboard Integration

Dashboard at `src/data-dashboard/` calls this backend for:
- Storage account configuration retrieval
- Transfer status via EDC APIs (not direct backend call)

### EDC Connector Integration

EDC Connector at `src/edc-connector/` triggers this backend via:
- Callback mechanism on transfer completion
- EDR token provision for data access

## Example Response

Successful callback response:

```json
{
  "status": "success"
}
```

HTTP Status: `200 OK`

## Performance Considerations

- Large file downloads are streamed to S3 for memory efficiency
- Progress tracking available for downloads > 1GB
- Supports parallel uploads if multiple transfers complete simultaneously
- Timeout: 30 seconds per callback processing

## Security

- Authorization codes from EDC are used for provider authentication
- S3 credentials loaded from environment (not committed to repository)
- Internal query parameters are filtered and removed from storage paths
- File paths are sanitized against path traversal attacks

## Support

For issues or questions:
- Check logs in Docker container
- Verify S3 configuration
- Ensure EDC Connector is properly configured with callback URLs
- Review Data Dashboard logs for transfer initiation details
