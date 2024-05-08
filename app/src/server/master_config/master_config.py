import json
from typing import Any
from app.src import env
from app.src.butter.checks import check_required
from app.src.server.master_config.bot_conf import BotConf
from app.src.server.master_config.tg_bot_conf_view import TgBotConfView


class MasterConfig:
    class Modifier:
        def __init__(self, mem: list[dict[str, Any]]):
            self._mem = mem

        def _save(self):
            with open(env.MAIN_CONFIG, "w") as f:
                json.dump(self._mem[0], f, indent=4)

        def enable_in_group(self, bot_id: str, chat_id: str):
            a_set = set(self._mem[0][bot_id]["tao_bot"]["chats"])
            a_set.add(chat_id)
            self._mem[0][bot_id]["tao_bot"]["chats"] = list(a_set)
            self._save()

        def disable_for_group(self, bot_id: str, chat_id: str):
            a_set = set(self._mem[0][bot_id]["tao_bot"]["chats"])
            a_set.remove(chat_id)
            self._mem[0][bot_id]["tao_bot"]["chats"] = list(a_set)
            self._save()

        def enable_for_username(self, bot_id: str, username: str):
            a_set = set(self._mem[0][bot_id]["tao_bot"]["users"])
            a_set.add(username)
            self._mem[0][bot_id]["tao_bot"]["users"] = list(a_set)
            self._save()

        def disable_for_username(self, bot_id: str, username: str):
            a_set = set(self._mem[0][bot_id]["tao_bot"]["users"])
            a_set.remove(username)
            self._mem[0][bot_id]["tao_bot"]["users"] = list(a_set)
            self._save()

        def set_number_of_messages_per_completion(self, bot_id: str, value: int):
            self._mem[0][bot_id]["tao_bot"]["messages_per_completion"] = value
            self._save()
   
    def __init__(self):
        with open(env.MAIN_CONFIG, "r") as f:
            self._mem: list[dict[str, Any]] = [{}]
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
    
    def modifier(self) -> Modifier:
        return MasterConfig.Modifier(self._mem)
