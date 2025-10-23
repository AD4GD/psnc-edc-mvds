from typing import Optional

import logging
from api.core.settings import DigitalWalletSettings
from api.models.db.participant import Participant
from api.exceptions.registration_service_exceptions import RecordNotFoundException
from .postgres_service import async_postgres_service

logger = logging.getLogger(__name__)

class DigitalWalletService:
    """ Synchronous service for interacting with Digital Wallet of chosen participant. """

    def __init__(self, participant_url: Optional[str] = None, participant_did: Optional[str] = None):
        self.endpoint = DigitalWalletSettings.dw_endpoint
        if participant_url:
            self.participant_url = participant_url
        elif participant_did:
            participant : Optional[Participant] = async_postgres_service.get_participant_by_did(participant_did)
            if not participant or not participant.protocol_url:
                raise RecordNotFoundException(f"Participant with DID {participant_did} not found or has no Digital Wallet endpoint")
            self.participant_url = participant.protocol_url
        else:
            raise ValueError("Either participant_url or participant_did must be provided")

    @property
    def dw_endpoint(self) -> str:
        return self.endpoint


dw_service = DigitalWalletService()
