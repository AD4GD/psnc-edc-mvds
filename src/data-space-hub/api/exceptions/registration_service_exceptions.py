"""
Custom exceptions for the Registration Service.
"""

from typing import Optional


class ProjectNameException(Exception):
    """Base exception for all PDF Converter service related errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class RecordNotFoundException(ProjectNameException):
    """Exception raised when record is not found."""

    def __init__(
        self,
        message: str = "Record not found",
        task_id: Optional[str] = None,
    ):
        details = {}
        if task_id:
            details["task_id"] = task_id

        super().__init__(message=message, status_code=404, details=details)


class ServiceUnavailableException(ProjectNameException):
    """Exception raised when a service is unavailable."""

    def __init__(self, message: str = "Service is unavailable"):
        super().__init__(message=message, status_code=503)


class ValidationException(ProjectNameException): # TODO correct
    """ Exception raised for validation errors. """

    def __init__(
        self,
        message: str = "Validation error",
        filename: Optional[str] = None,
        original_error: Optional[Exception] = None,
        field: Optional[str] = None,
    ):
        details = {}
        if filename:
            details["filename"] = filename
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        if field:
            details["field"] = field

        super().__init__(message=message, status_code=422, details=details)
