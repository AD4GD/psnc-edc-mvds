from fastapi import Header, HTTPException, Depends
from settings import Settings


async def verify_api_key(x_api_key: str = Header(None, alias="x-api-key")):
    """Dependency: Sprawdź API key z headera."""
    if not x_api_key or x_api_key != Settings.x_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
