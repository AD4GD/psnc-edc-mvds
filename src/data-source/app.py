from typing import Optional

from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/data/{extra_path:path}")
async def get_data(extra_path: str, request: Request):
    # Get query parameters
    query_params = dict(request.query_params)

    # Get headers
    headers = dict(request.headers)

    # Return JSON response showing request data
    return {"extra_path": extra_path, "query_params": query_params, "headers": headers}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
