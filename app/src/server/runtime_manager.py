import multiprocessing
from multiprocessing import synchronize
import os
from typing import Optional
from app.src.butter.checks import check_required
from app.src.server.api.internal_api_client import InternalApiClient
from app.src.server.master_config.bot_conf import BotConf
from app.src.server.master_config.tg_bot_conf import TgBotConf
from app.src.server.targets.tg_bot_target import TgBotTarget
from app.src import env
from app.src.server.master_config.master_config import MasterConfig


class RuntimeManager:
    def __init__(self, master_config: MasterConfig):
        self._master_config = check_required(master_config, "main_config", MasterConfig)
        self._state: dict[str, tuple[multiprocessing.Process, synchronize.Event]] = {}

    def start_all(self):
        for bot_conf in self._master_config.bots():
            self.start(bot_conf)

    def stop_all(self):
        for bot_conf in self._master_config.bots():
            self.stop(bot_conf.bot_id())

    def start(self, bot_conf: BotConf):
        if isinstance(bot_conf, TgBotConf):
            bot = TgBotTarget(bot_conf, InternalApiClient(bot_conf.bot_id(), self._master_config))
            stop_event: synchronize.Event = multiprocessing.Event()
            this_pid: int = os.getpid()
            if env.DEBUG:
                bot.run(stop_event, this_pid, is_subprocess=False)
            else:
                process = multiprocessing.Process(target=bot.run, args=(stop_event, this_pid, True))
                process.start()
                self._state[bot_conf.bot_id()] = (process, stop_event)
        else:
            raise NotImplementedError(
                f"Bot type {bot_conf.__class__.__name__} is not supported"
            )
        
    def stop(self, bot_id: Optional[str]):
        if bot_id is None:
            return
        if bot_id in self._state:
            process, stop_event = self._state[bot_id]
            stop_event.set()
            process.join()
            del self._state[bot_id]
