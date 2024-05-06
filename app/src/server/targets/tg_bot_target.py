import asyncio
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
from app.src.server.api.api_client import ApiClient
from app.src.server.master_config.tg_bot_conf import TgBotConf


class TgBotTarget:
    def __init__(self, bot_conf: TgBotConf, api_client: ApiClient):
        self._bot_conf: TgBotConf = check_required(bot_conf, "bot_conf", TgBotConf)
        self._api_client: ApiClient = check_required(
            api_client, "api_client", ApiClient
        )
        self._should_stop: bool = False

    def start(self):
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
        application = TgApplication(tao_bot, bot_commands, tg_token)

        if not in_test_mode():

            async def wait_for_stop():
                while not self._should_stop:
                    await asyncio.sleep(1)
                # This will stop asyncio loop of this thread
                application.stop()

            loop = asyncio.new_event_loop()
            asyncio.ensure_future(wait_for_stop(), loop=loop)
            application.start()

    def stop(self):
        self._should_stop = True
