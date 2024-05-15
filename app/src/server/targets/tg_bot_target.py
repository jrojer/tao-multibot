import asyncio
from multiprocessing import synchronize
import os
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.in_memory_chat_messages_repository import (
    InMemoryChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.postgres_chat_messages_repository import (
    PostgresChatMessagesRepository,
)
from app.src.bot.tao_bot.tao_bot import TaoBot
from app.src.bot.tao_bot.tao_bot_commands import TaoBotCommands
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.butter.checks import check_required
from app.src import env
from app.src.gpt.gpt_completer import GptCompleter
from app.src.gpt.gpt_conf import GptConf
from app.src.gpt.gpt_gateway import GptGateway
from app.src.gpt.openai_gpt_completer import OpenaiGptCompleter
from app.src.heads.tg_bot.v1.tg_application import TgApplication
from app.src.observability.logger import Logger
from app.src.server.api.conf_client import ConfClient
from app.src.server.master_config.openai_conf_client import GptConfClient
from app.src.server.master_config.tao_bot_conf_client import TaoBotConfClient


logger = Logger(__name__)


class TgBotTarget:
    def __init__(self, conf_client: ConfClient, telegram_token: str, bot_id: str):
        self._conf_client: ConfClient = check_required(
            conf_client, "conf_client", ConfClient
        )
        self._telegram_token = check_required(telegram_token, "telegram_token", str)
        self._bot_id = check_required(bot_id, "bot_id", str)
        self._should_stop: bool = False

    def run(
        self, stop_event: synchronize.Event, parent_id: int, is_subprocess: bool = False
    ):
        gpt_conf: GptConf = GptConfClient(self._conf_client, self._bot_id)
        tao_bot_conf: TaoBotConf = TaoBotConfClient(self._conf_client, self._bot_id)

        if env.POSTGRES_ENABLED():
            repo: ChatMessagesRepository = PostgresChatMessagesRepository(
                host=env.POSTGRES_HOST(),
                port=env.POSTGRES_PORT(),
                user=env.POSTGRES_USER(),
                password=env.POSTGRES_PASSWORD(),
                schemas=env.POSTGRES_SCHEMAS(),
            )
        else:
            repo: ChatMessagesRepository = InMemoryChatMessagesRepository()
        gpt_completer: GptCompleter = OpenaiGptCompleter(gpt_conf)
        gpt_gateway: GptGateway = GptGateway(gpt_completer)
        tao_bot: TaoBot = TaoBot(repo, gpt_gateway, tao_bot_conf)
        bot_commands: TaoBotCommands = TaoBotCommands(
            self._conf_client, tao_bot_conf, gpt_conf
        )
        application = TgApplication(
            tao_bot, bot_commands, self._telegram_token, gpt_conf.token()
        )

        if not env.in_test_mode():
            this_pid: int = os.getpid()

            async def wait_for_stop():
                while not stop_event.is_set() and (
                    not is_subprocess or this_pid != parent_id
                ):
                    await asyncio.sleep(1)
                logger.info(
                    f"Stopping bot {self._bot_id}, pid {this_pid} of parent {parent_id}"
                )
                # NOTE: This is effectively `asyncio.get_running_loop().stop()`
                application.stop()

            loop = asyncio.get_event_loop()
            asyncio.ensure_future(wait_for_stop(), loop=loop)
            logger.info(
                f"Starting bot {self._bot_id}, pid {this_pid} of parent {parent_id}"
            )
            application.start()
