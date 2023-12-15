from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import uvicorn
import os
import json
import datetime
import magic
import mimetypes

app = FastAPI()

class RequestData(BaseModel):
    endpoint: str
    authKey: str
    authCode: str


@app.post("/edr-endpoint")
async def edr_endpoint(request_data: RequestData):
    print("Entering edr endpoint")

    if not request_data.endpoint or not request_data.authKey or not request_data.authCode:
        return JSONResponse(content={'error': 'Missing or invalid endpoint, authKey or authCode parameters.'}, status_code=400)

    headers = {request_data.authKey: request_data.authCode}
    async with httpx.AsyncClient() as client:
        response = await client.get(request_data.endpoint, headers=headers)

    content_type = response.headers.get('content-type')

    print("Start downloading...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join("data", f"{timestamp}.bin")

    with open(filename, 'wb') as f:
        f.write(response.content)
    
    _mime = magic.from_buffer(response.content, mime=True)
    _ext = mimetypes.guess_extension(_mime)
    print(_mime, _ext)

    if _ext :# and content_type and content_type != "application/octet-stream":
        final_filename = os.path.join("data", f"{timestamp}{_ext}")
    else:
        final_filename = os.path.join("data", f"{timestamp}.bin")

    os.rename(filename, final_filename)
    print("Download finished. Filename: " + final_filename)
 
    return JSONResponse(content={'status': 'success'}, status_code=200)

if __name__ == '__main__':
    if not os.path.exists("data"):
        os.makedirs("data")
    uvicorn.run(app, host='0.0.0.0', port=4000)

