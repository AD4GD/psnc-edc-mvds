from fastapi import Header, HTTPException
from settings import MailSettings


async def verify_api_key(X_API_KEY: str = Header(None, alias="x-api-key")):
    """Dependency: Sprawdź API key z headera."""
    if not X_API_KEY or X_API_KEY != MailSettings.X_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return X_API_KEY
