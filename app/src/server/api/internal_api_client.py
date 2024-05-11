from app.src.butter.checks import check_required
from app.src.server.api.api_client import ApiClient
from app.src.server.master_config.master_config import MasterConfig

# TODO: client should be only remote
class InternalApiClient(ApiClient):
    def __init__(self, bot_id: str, master_config: MasterConfig):
        self._modifier = master_config.modifier()
        self._bot_id = check_required(bot_id, "bot_id", str)

    def enable_in_group(self, chat_id: str):
        self._modifier.enable_in_group(self._bot_id, chat_id)

    def disable_for_group(self, chat_id: str):
        self._modifier.enable_in_group(self._bot_id, chat_id)

    def enable_for_username(self, username: str):
        self._modifier.enable_for_username(self._bot_id, username)

    def disable_for_username(self, username: str):
        self._modifier.disable_for_username(self._bot_id, username)

    def set_number_of_messages_per_completion(self, value: int):
        self._modifier.set_number_of_messages_per_completion(self._bot_id, value)
