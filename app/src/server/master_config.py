import json
from typing import Any
from app.src import env
from app.src.butter.checks import check_required
from app.src.server.bot_conf import BotConf, TgBotConf

class MasterConfig:
    def __init__(self):
        with open(env.MAIN_CONFIG, "r") as f:
            self._mem: list[dict[dict[str, Any]]] = [None]
            self._mem[0] = check_required(json.load(f), "config", dict)

    def bot_conf(self, bot_id: str) -> BotConf:
        mem = self._mem
        if mem[0][bot_id]["type"] == "tg_bot":

            class TgBotConfView(TgBotConf):
                def _conf(self):
                    return mem[0][bot_id]["tg_bot"]
                
                def bot_id(self) -> str:
                    return bot_id

                def username(self) -> str:
                    return self._conf()["username"]

                def chats(self) -> list[str]:
                    return self._conf()["chats"]

                def admins(self) -> list[str]:
                    return self._conf()["admins"]

                def users(self) -> list[str]:
                    return self._conf()["users"]

                def token(self) -> str:
                    return self._conf()["token"]

            return TgBotConfView()

        else:
            raise NotImplementedError(
                f"Bot type {self._mem[0][bot_id]['type']} is not supported"
            )

    def bots(self) -> list[BotConf]:
        return [self.bot_conf(bot_id) for bot_id in self._mem[0].keys()]
