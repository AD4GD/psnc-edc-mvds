"""
Exception handlers for the FastAPI embeddings service.
"""
from api.core.logging_config import setup_logging
from api.exceptions.registration_service_exceptions import ProjectNameException
from api.models.dto.error_responses import ErrorResponse, ValidationErrorResponse
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DataError, IntegrityError

logger = setup_logging()
# TODO zabawa z łapaniem błędów


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the app."""

    @app.exception_handler(ProjectNameException)
    async def registration_service_exception_handler(request: Request, exc: ProjectNameException) -> JSONResponse:
        """Handle custom ProjectName service exceptions."""

        logger.error(
            f"Project Name Exception occurred: {exc.message}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error=exc.error_code, message=exc.message)

        return JSONResponse(status_code=exc.status_code, content=error_response.model_dump())

    @app.exception_handler(DataError)
    async def data_error_exception_handler(request: Request, exc: DataError) -> JSONResponse:
        """Handle custom ProjectName service exceptions."""

        error_message = str(exc.orig) if exc.orig else str(exc)
        error_message = error_message.split("\n", maxsplit=1)[0]

        logger.error(
            f"DataError occurred: {error_message}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error="Data Error", message=error_message, content={})

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump())

    @app.exception_handler(IntegrityError)
    async def integrity_error_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        """Handle custom ProjectName service exceptions."""
        error_message = str(exc.orig) if exc.orig else str(exc)
        error_message = error_message.split("\n", maxsplit=1)[0]

        logger.error(
            f"IntegrityError occurred: {error_message}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error="Integrity Error", message=error_message, content={})

        return JSONResponse(status_code=400, content=error_response.model_dump())  # Bad Request

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""

        field_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors.append({"field": field_path, "message": error["msg"], "type": error["type"]})

        logger.error(
            f"Request Validation error occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "validation_errors": field_errors,
            },
        )

        first_error = field_errors[0] if field_errors else {}
        error_response = ValidationErrorResponse(
            error="Request Validation Error",
            message=first_error.get("message", "Invalid input provided"),
            field=first_error.get("field"),
        )

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump())

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic ValidationError (different from RequestValidationError)."""

        logger.error(
            f"Pydantic ValidationError occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "validation_errors": exc.errors(),
            },
        )

        first_error = exc.errors()[0] if exc.errors() else {}
        field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))

        error_response = ValidationErrorResponse(
            error="Validation Error",
            message=first_error.get("msg", "Invalid input provided"),
            field=field_path or None,
        )

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.model_dump())

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
        """Handle Pydantic Response validation errors."""

        field_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors.append({"field": field_path, "message": error["msg"], "type": error["type"]})

        logger.error(
            f"Response Validation error occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "validation_errors": field_errors,
            },
        )

        first_error = field_errors[0] if field_errors else {}
        error_response = ValidationErrorResponse(
            error="Response Validation Error",
            message=first_error.get("message", "Invalid response model"),
            field=first_error.get("field"),
        )

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump())

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""

        logger.exception(
            f"Unexpected error occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(
            error="General Exception", message="An unexpected error occurred. Please try again later.", content=None
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )
