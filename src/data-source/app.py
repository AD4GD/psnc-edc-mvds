import csv
from io import StringIO

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, StreamingResponse

app = FastAPI()

IP = "0.0.0.0/0"  # nosec
PORT = 5000  # nosec


@app.get("/data/{extra_path:path}")
async def get_data(extra_path: str, request: Request):
    # Get query parameters
    query_params = dict(request.query_params)

    # Get headers
    headers = dict(request.headers)

    # Return JSON response showing request data
    return {"extra_path": extra_path, "query_params": query_params, "headers": headers}


# Endpoint returning plain text
@app.get("/formats/text", response_class=PlainTextResponse)
async def get_text():
    return "This is plain text data."


# Endpoint returning HTML content
@app.get("/formats/html", response_class=HTMLResponse)
async def get_html():
    html_content = """
    <html>
        <head><title>HTML Response</title></head>
        <body>
            <h1>This is an HTML response</h1>
            <p>Served by FastAPI</p>
        </body>
    </html>
    """
    return html_content


# Endpoint returning binary data (e.g., an image or file)
@app.get("/formats/binary")
async def get_binary():
    binary_data = b"Binary data content here"  # Example binary content
    return Response(content=binary_data, media_type="application/octet-stream")


# Endpoint returning a file (e.g., a downloadable file)
@app.get("/formats/file")
async def get_file():
    file_path = "./assets/example.txt"  # Path to a file on your server
    return FileResponse(path=file_path, media_type="application/octet-stream", filename="example.txt")


# Endpoint returning streaming data
@app.get("/formats/stream")
async def get_stream():
    def stream_data():
        for i in range(5):  # Simulating streaming of data chunks
            yield f"Chunk {i}\n"

    return StreamingResponse(stream_data(), media_type="text/plain")


# Endpoint returning CSV data
@app.get("/formats/csv")
async def get_csv():
    # Generate CSV data in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Column 1", "Column 2", "Column 3"])
    writer.writerow([1, 2, 3])
    writer.writerow([4, 5, 6])
    writer.writerow([7, 8, 9])
    output.seek(0)

    # Stream the CSV content
    return StreamingResponse(
        output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=IP, port=PORT)
