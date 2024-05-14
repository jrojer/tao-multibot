from telegram.error import NetworkError
from telegram.ext import ContextTypes

from app.src.observability.logger import Logger

logger = Logger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    if type(context.error) == NetworkError:
        logger.error("Network error occurred. Retrying to connect...")
