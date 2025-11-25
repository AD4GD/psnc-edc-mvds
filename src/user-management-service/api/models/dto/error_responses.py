"""
Error response models for the Registration Service API.
"""

from typing import Any, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response model for the API."""

    error: str
    message: str
    content: Any


class ValidationErrorResponse(BaseModel):
    """Error response model for validation errors."""

    error: str
    message: str
    field: Optional[str] = None
