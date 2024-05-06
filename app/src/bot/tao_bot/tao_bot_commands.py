from app.src.bot.handlers.start_handler import get_start_handler
from app.src.bot.handlers.update_access_handler import get_update_access_handler
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_response import TaoBotResponse, ignore, reply_text
from app.src.butter.checks import check_required
from app.src.gpt.gpt_conf import GptConf
from app.src.observability.logger import Logger
from app.src.bot.handlers.enable_in_current_group_handler import (
    get_disable_in_group_handler,
    get_enable_in_group_handler,
)
from app.src.bot.handlers.help_handler import get_help_command_hadler
from app.src.bot.handlers.setters import (
    get_set_number_of_messages_for_completion_handler,
)
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.bot.tao_bot.ui_text import (
    CONFIG,
    DISASBLE_IN_CURRENT_GROUP,
    ENABLE_IN_CURRENT_GROUP,
    SET_NUMBER_OF_MESSAGES_PER_COMPLETION,
    START,
    UPDATE_ACCESS,
)
from app.src.server.api.api_client import ApiClient

logger = Logger(__name__)


def command(bot_username: str, cmd: str) -> str:
    return "/" + cmd + "@" + bot_username


def extract_cmd(post: str) -> str:
    # extracts cmd from '/cmd@bot_username'
    return post.split("@")[0].split("/")[1]


class TaoBotCommands:
    def __init__(
        self, client: ApiClient, tao_bot_conf: TaoBotConf, gpt_conf: GptConf
    ) -> None:
        self._client = check_required(client, "client", ApiClient)
        self._tao_bot_conf = check_required(tao_bot_conf, "tao_bot_conf", TaoBotConf)
        self._gpt_conf = check_required(gpt_conf, "gpt_conf", GptConf)

    def _commands(self):
        return {
            ENABLE_IN_CURRENT_GROUP: get_enable_in_group_handler(self._client),
            DISASBLE_IN_CURRENT_GROUP: get_disable_in_group_handler(self._client),
            UPDATE_ACCESS: get_update_access_handler(self._client),
            START: get_start_handler(),
            CONFIG: get_help_command_hadler(self._tao_bot_conf, self._gpt_conf),
            SET_NUMBER_OF_MESSAGES_PER_COMPLETION: get_set_number_of_messages_for_completion_handler(
                self._client
            ),
            # TODO: add setters for GPT settings if demanded
        }

    def _is_authorised(self, update: TaoBotUpdate) -> bool:
        cfg = self._client
        return (
            update.chat_id() is not None
            and update.chat_id() == cfg.get_control_group()
            or update.from_user() in cfg.get_admins()
        )

    def _is_command_for(self, bot_username: str, update: TaoBotUpdate) -> bool:
        if update.post() is None:
            return False
        for cmd in self._commands().keys():
            if update.post().startswith(command(bot_username, cmd)):
                return True
        return False

    def _run_command_for(self, bot_username: str, update: TaoBotUpdate) -> str:
        if not self._is_command_for(bot_username, update):
            raise AssertionError("Programmer error: unchecked command")
        return self._commands()[extract_cmd(update.post())](update)

    def handle_command(
        self, bot_username: str, tao_update: TaoBotUpdate
    ) -> TaoBotResponse:
        if self._is_command_for(bot_username, tao_update):
            if self._is_authorised(tao_update):
                command_reply = self._run_command_for(bot_username, tao_update)
                return reply_text(command_reply)
            else:
                logger.warning(
                    f'An attempt to call "{tao_update.post()}" from {tao_update.chat_id()}. Skipping execution.'
                )
        return ignore()
