import json
from pathlib import Path
from typing import Any
from app.src.butter.checks import check_required


class MasterConfig:
    class Modifier:
        def __init__(
            self, deserialised_json_config: dict[str, Any], path_to_master_conf: Path
        ):
            self._d: dict[str, Any] = check_required(
                deserialised_json_config, "config", dict
            )
            self._path_to_master_conf: str = check_required(
                path_to_master_conf, "path_to_master_conf", Path
            )

        def _save(self):
            with open(self._path_to_master_conf, "w") as f:
                json.dump(self._d, f, indent=4, ensure_ascii=False)

        def enable_in_group(self, bot_id: str, chat_id: str):
            a_set = set(self._d[bot_id]["tao_bot"]["chats"])
            a_set.add(chat_id)
            self._d[bot_id]["tao_bot"]["chats"] = list(a_set)
            self._save()

        def disable_for_group(self, bot_id: str, chat_id: str):
            a_set = set(self._d[bot_id]["tao_bot"]["chats"])
            a_set.remove(chat_id)
            self._d[bot_id]["tao_bot"]["chats"] = list(a_set)
            self._save()

        def enable_for_username(self, bot_id: str, username: str):
            a_set = set(self._d[bot_id]["tao_bot"]["users"])
            a_set.add(username)
            self._d[bot_id]["tao_bot"]["users"] = list(a_set)
            self._save()

        def disable_for_username(self, bot_id: str, username: str):
            a_set = set(self._d[bot_id]["tao_bot"]["users"])
            a_set.remove(username)
            self._d[bot_id]["tao_bot"]["users"] = list(a_set)
            self._save()

        def set_number_of_messages_per_completion(self, bot_id: str, value: int):
            self._d[bot_id]["tao_bot"]["messages_per_completion"] = value
            self._save()

    def __init__(self, path_to_master_conf: Path):
        self._path_to_master_conf = check_required(
            path_to_master_conf, "path_to_master_conf", Path
        )
        with open(path_to_master_conf, "r") as f:
            self._d: dict[str, Any] = check_required(json.load(f), "config", dict)

    def bot_conf(self, bot_id: str) -> dict[str, Any]:
        tc = self._d[bot_id]["tao_bot"]
        gc = self._d[bot_id]["gpt"]
        return {
            "bot_id": bot_id,
            "type": self._d[bot_id]["type"],
            "token": self._d[bot_id]["token"],
            "tao_bot": {
                "username": tc["username"],
                "chats": tc["chats"],
                "admins": tc["admins"],
                "users": tc["users"],
                "control_chat_id": tc["control_chat_id"],
                "system_prompt": tc["system_prompt"],
                "messages_per_completion": tc["messages_per_completion"],
                "bot_mention_names": tc["bot_mention_names"],
            },
            "gpt": {
                "token": gc["token"],
                "model": gc["model"],
                "temperature": gc["temperature"],
                "max_tokens": gc["max_tokens"],
                "top_p": gc["top_p"],
                "frequency_penalty": gc["frequency_penalty"],
                "presence_penalty": gc["presence_penalty"],
            },
        }

    def bots(self) -> list[dict[str, Any]]:
        return [self.bot_conf(bot_id) for bot_id in self._d.keys()]

    def modifier(self) -> Modifier:
        return MasterConfig.Modifier(self._d, self._path_to_master_conf)
