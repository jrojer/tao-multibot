import asyncio
from multiprocessing import synchronize
import os
import threading
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.in_memory_chat_messages_repository import (
    InMemoryMessagesRepository,
)
from app.src.bot.tao_bot.tao_bot import TaoBot
from app.src.bot.tao_bot.tao_bot_commands import TaoBotCommands
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.butter.checks import check_required
from app.src.env import in_test_mode
from app.src.gpt.gpt_completer import GptCompleter
from app.src.gpt.gpt_conf import GptConf
from app.src.gpt.gpt_gateway import GptGateway
from app.src.gpt.openai_gpt_completer import OpenaiGptCompleter
from app.src.heads.tg_bot.v1.tg_application import TgApplication
from app.src.observability.logger import Logger, reconfigure_logging
from app.src.server.api.api_client import ApiClient
from app.src.server.master_config.tg_bot_conf import TgBotConf


logger = Logger(__name__)


class TgBotTarget:
    def __init__(self, bot_conf: TgBotConf, api_client: ApiClient):
        self._bot_conf: TgBotConf = check_required(bot_conf, "bot_conf", TgBotConf)
        self._api_client: ApiClient = check_required(
            api_client, "api_client", ApiClient
        )
        self._should_stop: bool = False

    def run(self, stop_event: synchronize.Event, parent_id: int, is_subprocess:bool=False):
        gpt_conf: GptConf = self._bot_conf.openai_conf()
        tao_bot_conf: TaoBotConf = self._bot_conf.tao_bot_conf()

        repo: ChatMessagesRepository = InMemoryMessagesRepository()
        tg_token: str = self._bot_conf.token()
        gpt_completer: GptCompleter = OpenaiGptCompleter(gpt_conf)
        gpt_gateway: GptGateway = GptGateway(gpt_completer)
        tao_bot: TaoBot = TaoBot(repo, gpt_gateway, tao_bot_conf)
        bot_commands: TaoBotCommands = TaoBotCommands(
            self._api_client, tao_bot_conf, gpt_conf
        )
        application = TgApplication(tao_bot, bot_commands, tg_token, gpt_conf.token())

        if not in_test_mode():
            this_pid: int = os.getpid()
            async def wait_for_stop():
                while not stop_event.is_set() and (not is_subprocess or this_pid != parent_id):
                    await asyncio.sleep(1)
                logger.info(f"Stopping bot {self._bot_conf.bot_id()}, pid {this_pid} of parent {parent_id}")
                # NOTE: This is effectively `asyncio.get_running_loop().stop()`
                application.stop()

            loop = asyncio.get_event_loop()
            asyncio.ensure_future(wait_for_stop(), loop=loop)
            threading.current_thread().name = f"{self._bot_conf.bot_id()}_thread"
            reconfigure_logging()
            logger.info(f"Starting bot {self._bot_conf.bot_id()}, pid {this_pid} of parent {parent_id}")
            application.start()
