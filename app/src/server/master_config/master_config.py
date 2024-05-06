import json
from typing import Any
from app.src import env
from app.src.butter.checks import check_required
from app.src.server.master_config.bot_conf import BotConf
from app.src.server.master_config.tg_bot_conf_view import TgBotConfView


class MasterConfig:
    def __init__(self):
        with open(env.MAIN_CONFIG, "r") as f:
            self._mem: list[dict[dict[str, Any]]] = [None]
            self._mem[0] = check_required(json.load(f), "config", dict)

    def bot_conf(self, bot_id: str) -> BotConf:
        if "tg_bot" in self._mem[0][bot_id]:
            return TgBotConfView(self._mem, bot_id)
        else:
            raise NotImplementedError(
                f"No known bot type for bot_id {bot_id}"
            )

    def bots(self) -> list[BotConf]:
        return [self.bot_conf(bot_id) for bot_id in self._mem[0].keys()]
