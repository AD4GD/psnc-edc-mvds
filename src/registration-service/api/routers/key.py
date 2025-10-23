from __future__ import annotations
from typing import Any
import json
import logging

from fastapi import APIRouter, status

from api.models.dto.responses import SimpleMessageResponse
from api.core.settings import ProjectSettings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/signed", tags=["key", "publickey"])


@router.get(
    f"/publickey/{ProjectSettings.issuer_did}",
    response_model=SimpleMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Download issuer public key",
)
def test_endpoint():
    # TODO implement actual public key retrieval
    """
    Test endpoint with various stages
    """
    return SimpleMessageResponse(message="Test endpoint reached successfully")
