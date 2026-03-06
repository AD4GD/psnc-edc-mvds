"""
Exception handlers for the FastAPI embeddings service.
"""
from api.core.logging_config import setup_logging
from api.exceptions.registration_service_exceptions import (
    ProjectNameException,
    RecordAlreadyExistsException,
    RecordNotFoundException,
    UnauthorizedException,
)
from api.models.dto.error_responses import ErrorResponse, ValidationErrorResponse
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse, Response
from keycloak.exceptions import KeycloakPostError
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
    @app.exception_handler(IntegrityError)
    async def data_error_exception_handler(request: Request, exc: DataError | IntegrityError) -> JSONResponse:
        """Handle custom ProjectName service exceptions."""

        error_message = str(exc.orig) if exc.orig else str(exc)
        error_message = error_message.split("\n", maxsplit=1)[0]

        logger.error(
            f"{exc.__class__.__name__} occurred: {error_message}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error=exc.__class__.__name__, message=error_message, content={})

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump())

    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ResponseValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError | ResponseValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""

        field_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors.append({"field": field_path, "message": error["msg"], "type": error["type"]})

        logger.error(
            f"{exc.__class__.__name__} error occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "validation_errors": field_errors,
            },
        )

        first_error = field_errors[0] if field_errors else {}
        error_response = ValidationErrorResponse(
            error=exc.__class__.__name__,
            message=first_error.get("message", "Validation error for incoming data"),
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

    @app.exception_handler(RecordAlreadyExistsException)
    async def record_already_exists_exception_handler(request: Request, exc: RecordAlreadyExistsException) -> JSONResponse:
        """Handle unexpected exceptions."""

        logger.error(
            f"{exc.name} occurred: {exc.to_dict()}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error=exc.name, message=exc.message, content=exc.to_dict())

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump(),
        )

    @app.exception_handler(RecordNotFoundException)
    async def record_not_found_exception_handler(request: Request, exc: RecordNotFoundException) -> Response:
        """Handle Not Found exception."""

        logger.error(
            f"{exc.name} occurred: {exc.to_dict()}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        return Response(status_code=exc.status_code, content="Record not found")

    @app.exception_handler(KeycloakPostError)
    async def keycloak_post_exception_handler(request: Request, exc: KeycloakPostError):
        raise UnauthorizedException(message=str(exc), action="Keycloak not available for this user")

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(request: Request, warn: UnauthorizedException) -> JSONResponse:
        """Handle unexpected exceptions."""

        logger.warning(
            f"{warn.name} occurred: {warn.to_dict()}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Unautorized access")

    @app.exception_handler(KeyError)
    # @app.exception_handler(AttributeError)
    async def key_error_exception_handler(request: Request, exc: KeyError | AttributeError) -> JSONResponse:
        """Handle KeyError for filling json templates."""

        logger.error(
            f"{exc.__class__.__name__} occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error=exc.__class__.__name__, message=str(exc), content=None)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""

        logger.error(
            f"Unexpected error occurred: {exc}",
            extra={
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            },
        )

        error_response = ErrorResponse(error="General Exception", message="An unexpected error occurred. Please try again later.", content=None)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )
