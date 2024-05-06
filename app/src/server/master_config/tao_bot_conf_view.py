
from typing import Any

from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf


class TaoBotConfView(TaoBotConf):
    def __init__(self, mem: list[dict[dict[str, Any]]], bot_id: str):
        self._mem = mem
        self._bot_id = bot_id

    def _conf(self):
        return self._mem[0][self._bot_id]["tao_bot"]

    def bot_id(self) -> str:
        return self._bot_id

    def username(self) -> str:
        return self._conf()["username"]

    def chats(self) -> list[str]:
        return self._conf()["chats"]

    def admins(self) -> list[str]:
        return self._conf()["admins"]

    def users(self) -> list[str]:
        return self._conf()["users"]
