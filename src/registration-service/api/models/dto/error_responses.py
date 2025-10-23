"""
Error response models for the Registration Service API.
"""

from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response model for the API."""

    error: str
    message: str
    request_id: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Error response model for validation errors."""

    error: str
    message: str
    field: Optional[str] = None
    request_id: Optional[str] = None
