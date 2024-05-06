from app.src.butter.checks import check_required
from threading import Thread
from app.src.server.api.internal_api_client import InternalApiClient
from app.src.server.master_config.bot_conf import BotConf
from app.src.server.master_config.tg_bot_conf import TgBotConf
from app.src.server.targets.tg_bot_target import TgBotTarget

from app.src.server.master_config.master_config import MasterConfig


class RuntimeManager:
    def __init__(self, master_config: MasterConfig):
        self._master_config = check_required(master_config, "main_config", MasterConfig)
        self._state = {}

    def start_all(self):
        for bot_conf in self._master_config.bots():
            self.start(bot_conf)

    def stop_all(self):
        for bot_conf in self._master_config.bots():
            self.stop(bot_conf.bot_id())

    def start(self, bot_conf: BotConf):
        if isinstance(bot_conf, TgBotConf):
            bot = TgBotTarget(bot_conf, InternalApiClient(bot_conf.bot_id(), self._master_config))
            thread_name = f"{bot_conf.bot_id()}_thread"
            thread = Thread(target=bot.start, name=thread_name, daemon=True)
            thread.start()
            self._state[bot_conf.bot_id()] = (thread, bot)
        else:
            raise NotImplementedError(
                f"Bot type {bot_conf.__class__.__name__} is not supported"
            )
        
    def stop(self, bot_id: str):
        if bot_id in self._state:
            thread, bot = self._state[bot_id]
            bot.stop()
            thread.join()
            del self._state[bot_id]
