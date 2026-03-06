from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: str
    body_type: Literal["html", "plain"]


class SendEmailResponse(BaseModel):
    message: str
    code: Optional[int]
