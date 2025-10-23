"""
Exception handlers for the FastAPI embeddings service.
"""

import uuid

from api.core.logging import logger
from api.exceptions.registration_service_exceptions import ProjectNameException
from api.models.dto.error_responses import ErrorResponse, ValidationErrorResponse
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the app."""

    @app.exception_handler(ProjectNameException)
    async def registration_service_exception_handler(
        request: Request, exc: ProjectNameException
    ) -> JSONResponse:
        """Handle custom ProjectName service exceptions."""

        request_id = str(uuid.uuid4())
        logger.error(
            f"ProjectNameException occurred: {exc.message}",
            extra={
                "request_id": request_id,
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(
            error=exc.error_code, message=exc.message, request_id=request_id
        )

        return JSONResponse(
            status_code=exc.status_code, content=error_response.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""

        request_id = str(uuid.uuid4())

        field_errors = []
        for error in exc.errors():
            print(error)
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors.append(
                {"field": field_path, "message": error["msg"], "type": error["type"]}
            )

        logger.error(
            f"Validation error occurred: {exc}",
            extra={
                "request_id": request_id,
                "url": str(request.url),
                "method": request.method,
                "validation_errors": field_errors,
            },
        )

        first_error = field_errors[0] if field_errors else {}
        print(field_errors)
        error_response = ValidationErrorResponse(
            error="ValidationError",
            message=first_error.get("message", "Invalid input provided"),
            field=first_error.get("field"),
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump()
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic ValidationError (different from RequestValidationError)."""

        request_id = str(uuid.uuid4())

        logger.error(
            f"Pydantic ValidationError occurred: {exc}",
            extra={
                "request_id": request_id,
                "url": str(request.url),
                "method": request.method,
                "validation_errors": exc.errors(),
            },
        )

        first_error = exc.errors()[0] if exc.errors() else {}
        field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))

        error_response = ValidationErrorResponse(
            error="ValidationError",
            message=first_error.get("msg", "Invalid input provided"),
            field=field_path or None,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""

        request_id = str(uuid.uuid4())

        logger.exception(
            f"Unexpected error occurred: {exc}",
            extra={
                "request_id": request_id,
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred. Please try again later.",
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )
