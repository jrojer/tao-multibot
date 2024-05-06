from app.tao.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.tao.butter.checks import check_required, check_that
from app.tao.ui_text import CONFIG

from app.tao.tao_config import TaoConfig
from app.tao.observability.logger import Logger

import re

logger = Logger(__name__)


def extract_float(string):
    match = re.search(r"[+-]?\d+(\.\d+)?", string)
    if match:
        return float(match.group(0))
    else:
        return None


def extract_int(string):
    match = re.search(r"\d+", string)
    if match:
        return int(match.group(0))
    else:
        return None


def set_parameter(config: TaoConfig, chat_id, value, name) -> str:
    try:
        config.set_parameter(name, value)
        logger.info("chat_id %s %s set to %s", chat_id, name, value)
    except ValueError as e:
        return f"Cannot set value. {e}"
    return f"`{name}` set to {value}. /{CONFIG}"


def get_set_temperature_handler(config: TaoConfig):
    return lambda update: set_parameter(
        config, update.chat_id(), extract_float(update.post()), "temperature"
    )


def get_set_top_p_handler(config: TaoConfig):
    return lambda update: set_parameter(
        config, update.chat_id(), extract_float(update.post()), "top_p"
    )


def get_set_max_tokens_handler(config: TaoConfig):
    return lambda update: set_parameter(
        config, update.chat_id(), extract_int(update.post()), "max_tokens"
    )


def get_set_presence_penalty_handler(config: TaoConfig):
    return lambda update: set_parameter(
        config, update.chat_id(), extract_float(update.post()), "presence_penalty"
    )


def get_set_frequency_penalty_handler(config: TaoConfig):
    return lambda update: set_parameter(
        config, update.chat_id(), extract_float(update.post()), "frequency_penalty"
    )


def get_set_number_of_messages_for_completion_handler(config: TaoConfig):
    def handler(update: TaoBotUpdate) -> str:
        try:
            value = extract_int(update.post())
            config.set_number_of_messages_per_completion(value)
            logger.info("number_of_messages_for_completion set to %s", value)
            return f"`number_of_messages_for_completion` set to {value}. /{CONFIG}"
        except ValueError as e:
            return f"Cannot set value. {e}"

    return handler
