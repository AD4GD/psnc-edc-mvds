"""
Logging configuration for the embeddings service.
"""

import logfire
from api.core.settings import ProjectSettings

logfire.configure(
    service_name=ProjectSettings.service_name,
    send_to_logfire=False,
)

logger = logfire
# logger.instrument_asyncpg()
