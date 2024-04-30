from app.src.butter.checks import check_required
from app.src.server.bot_conf import BotConf, TgBotConf
from threading import Thread
from app.src.server.tg_bot import TgBot

from app.src.server.master_config import MasterConfig


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
            bot = TgBot(bot_conf)
            def target():
                bot.start()
            thread = Thread(target=target, name=bot_conf.bot_id(), daemon=True)
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
