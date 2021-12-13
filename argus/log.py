from logging.config import dictConfig
from argus.defs.logging import LOGGING_PROD
import logging

dictConfig(LOGGING_PROD)

log = logging.getLogger('argus')
