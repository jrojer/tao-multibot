from typing import Any
from app.src.server.api.conf_client import ConfClient
import requests


class HttpConfClient(ConfClient):
    def __init__(self, port: int, bot_id: str):
        self._port = port
        self._bot_id = bot_id

    def get_bot_conf(self) -> dict[str, Any]:
        url = f"http://localhost:{self._port}/api/bots/{self._bot_id}/conf"
        response = requests.get(url)
        return response.json()

    def enable_for_group(self, chat_id: str):
        url = f"http://localhost:{self._port}/api/bots/{self._bot_id}/chats/{chat_id}/enable"
        requests.post(url)

    def disable_for_group(self, chat_id: str):
        url = f"http://localhost:{self._port}/api/bots/{self._bot_id}/chats/{chat_id}/disable"
        requests.post(url)

    def enable_for_username(self, username: str):
        url = f"http://localhost:{self._port}/api/bots/{self._bot_id}/users/{username}/enable"
        requests.post(url)

    def disable_for_username(self, username: str):
        url = f"http://localhost:{self._port}/api/bots/{self._bot_id}/users/{username}/disable"
        requests.post(url)

    def set_number_of_messages_per_completion(self, value: int):
        url = f"http://localhost:{self._port}/api/bots/{self._bot_id}/conf/messages_per_completion"
        requests.post(url, json={"value": value})
    