import multiprocessing
from multiprocessing import synchronize
import os
from typing import Any, Optional
from app.src.butter.checks import check_required
from app.src.server.api.http_conf_client import HttpConfClient
from app.src.server.api.conf_client import ConfClient
from app.src.server.targets.tg_bot_target import TgBotTarget
from app.src.server.master_config.master_config import MasterConfig

multiprocessing.set_start_method("fork")

class RuntimeManager:
    def __init__(self, server_port: int, master_config: MasterConfig):
        self._server_port = server_port
        self._master_config: MasterConfig = check_required(master_config, "main_config", MasterConfig)
        self._state: dict[str, tuple[multiprocessing.Process, synchronize.Event]] = {}

    def start_all(self):
        for bot_conf in self._master_config.bots():
            self.start(bot_conf)

    def stop_all(self):
        for bot_conf in self._master_config.bots():
            self.stop(bot_conf["bot_id"])

    def start(self, bot_conf: dict[str, Any]):
        bot_id: str = bot_conf["bot_id"]
        if bot_conf["type"] == "tg_bot":
            conf_client: ConfClient = HttpConfClient(self._server_port, bot_id)
            bot = TgBotTarget(conf_client, bot_conf["token"], bot_id)
            stop_event: synchronize.Event = multiprocessing.Event()
            this_pid: int = os.getpid()
            process = multiprocessing.Process(target=bot.run, args=(stop_event, this_pid, True))
            process.start()
            self._state[bot_id] = (process, stop_event)
        else:
            raise NotImplementedError(
                f"Bot type {bot_conf["type"]} is not supported"
            )
        
    def stop(self, bot_id: Optional[str]):
        if bot_id is None:
            return
        if bot_id in self._state:
            process, stop_event = self._state[bot_id]
            stop_event.set()
            process.join()
            del self._state[bot_id]
