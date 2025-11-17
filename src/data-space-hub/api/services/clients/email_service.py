import json
from typing import List, Literal

import requests
from api.core.logging_config import setup_logging
from api.core.settings import EmailServiceSettings

logger = setup_logging()


class EmailService:
    def __init__(self):
        pass

    @staticmethod
    def send_email(recipients: List[str], subject: str, body: str, body_type: Literal["plain", "html"]):
        response = requests.post(
            url=EmailServiceSettings.email_svc_endpoint,
            data=json.dumps({"recipients": recipients, "subject": subject, "body": body, "body_type": body_type}),
            headers={"x-api-key": EmailServiceSettings.email_api_key},
        )
        return {"code": response.status_code, "message": response.text}
