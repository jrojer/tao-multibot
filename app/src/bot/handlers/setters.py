import re

from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.bot.tao_bot.ui_text import CONFIG
from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.api.conf_client import ConfClient

logger = Logger(__name__)


def _extract_int(string: str) -> int:
    match = re.search(r"\d+", string)
    if match:
        return int(match.group(0))
    else:
        raise ValueError("No integer found")


def get_set_number_of_messages_per_completion_handler(client: ConfClient):
    def handler(update: TaoBotUpdate) -> str:
        try:
            content: str = check_required(update.content(), "content", str)
            value = _extract_int(content)
            client.set_number_of_messages_per_completion(value)
            logger.info("number_of_messages_per_completion set to %s", value)
            return f"`number_of_messages_per_completion` set to {value}. /{CONFIG}"
        except ValueError as e:
            return f"Cannot set value. {e}"

    return handler
