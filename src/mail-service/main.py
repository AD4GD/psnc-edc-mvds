import asyncio
import time

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from fastapi_mail.errors import ConnectionErrors
from logging_config import setup_logging
from models import SendEmailRequest, SendEmailResponse
from pydantic import ValidationError
from security import verify_api_key
from settings import MailSettings  # pylint: disable=no-name-in-module
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

TIMEOUT_SECONDS = 5

logger = setup_logging()
limiter = Limiter(key_func=get_remote_address)
fm = FastMail(
    ConnectionConfig(
        MAIL_USERNAME=MailSettings.MAIL_USERNAME,
        MAIL_PASSWORD=MailSettings.MAIL_PASSWORD,
        MAIL_FROM=MailSettings.MAIL_FROM,
        MAIL_PORT=MailSettings.MAIL_PORT,
        MAIL_SERVER=MailSettings.MAIL_SERVER,
        MAIL_FROM_NAME=MailSettings.MAIL_FROM_NAME,
        MAIL_STARTTLS=MailSettings.MAIL_STARTTLS,
        MAIL_SSL_TLS=MailSettings.MAIL_SSL_TLS,
        USE_CREDENTIALS=MailSettings.USE_CREDENTIALS,
        VALIDATE_CERTS=MailSettings.VALIDATE_CERTS,
        TEMPLATE_FOLDER=MailSettings.TEMPLATE_FOLDER,
    )
)

app = FastAPI(title="Mail Service", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_methods=["POST"],
    allow_headers=["x-api-key", "*"],
)


@app.post("/email", response_model=SendEmailResponse, summary="Send email from request body")
@limiter.limit("5/minute")
@limiter.limit("500/hour")
async def send_email(body: SendEmailRequest, request: Request, api_key: str = Depends(verify_api_key)) -> JSONResponse:
    message = MessageSchema(subject=body.subject, recipients=body.recipients, body=body.body, subtype=body.body_type)
    try:
        start_time = time.time()
        await asyncio.wait_for(fm.send_message(message), timeout=TIMEOUT_SECONDS)
        send_time = time.time() - start_time

        logger.info(f"Email sent in {send_time:.2f}s")
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except ValidationError as e:
        logger.error(str(e))
        return JSONResponse(status_code=400, content={"message": "Bad email configuration"})
    except ConnectionErrors as e:
        logger.error(str(e))
        return JSONResponse(status_code=401, content={"message": "Bad credentials"})
    except asyncio.TimeoutError as e:
        logger.error(str(e))
        return JSONResponse(status_code=408, content={"message": "Request timeout - bad configuration"})
    except Exception as e:  # pylint: disable=W0718
        logger.critical(str(e))
        return JSONResponse(status_code=500, content={"message": "Error during sending an email"})
