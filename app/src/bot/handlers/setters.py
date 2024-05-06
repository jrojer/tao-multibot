import re

from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.bot.tao_bot.ui_text import CONFIG
from app.src.observability.logger import Logger
from app.src.server.api.api_client import ApiClient

logger = Logger(__name__)


def extract_int(string):
    match = re.search(r"\d+", string)
    if match:
        return int(match.group(0))
    else:
        return None


def get_set_number_of_messages_for_completion_handler(client: ApiClient):
    def handler(update: TaoBotUpdate) -> str:
        try:
            value = extract_int(update.post())
            client.set_number_of_messages_per_completion(value)
            logger.info("number_of_messages_for_completion set to %s", value)
            return f"`number_of_messages_for_completion` set to {value}. /{CONFIG}"
        except ValueError as e:
            return f"Cannot set value. {e}"

    return handler
