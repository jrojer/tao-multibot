from typing import Any
from app.src.server.api.conf_client import ConfClient

from app.src.server.master_config.master_config import MasterConfig

# NOTE: this is left for debugging purposes
class InternalConfClient(ConfClient):
    def __init__(self, master_conf: MasterConfig, bot_id: str):
        self._master_conf = master_conf
        self._bot_id = bot_id

    def get_bot_conf(self) -> dict[str, Any]:
        return self._master_conf.bot_conf(self._bot_id)

    def enable_for_group(self, chat_id: str):
        self._master_conf.modifier().enable_in_group(self._bot_id, chat_id)

    def disable_for_group(self, chat_id: str):
        self._master_conf.modifier().disable_for_group(self._bot_id, chat_id)

    def enable_for_username(self, username: str):
        self._master_conf.modifier().enable_for_username(self._bot_id, username)

    def disable_for_username(self, username: str):
        self._master_conf.modifier().disable_for_username(self._bot_id, username)

    def set_number_of_messages_per_completion(self, value: int):
        self._master_conf.modifier().set_number_of_messages_per_completion(self._bot_id, value)
    