from typing import Any
from app.src.server.api.conf_client import ConfClient


class MockConfClient(ConfClient):
    def __init__(self):
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_bot_conf(self) -> dict[str, Any]:
        self.calls.append(("get_bot_conf", {}))
        return {}

    def enable_for_group(self, chat_id: str):
        self.calls.append(("enable_for_group", {"chat_id": chat_id}))

    def disable_for_group(self, chat_id: str):
        self.calls.append(("disable_for_group", {"chat_id": chat_id}))

    def enable_for_username(self, username: str):
        self.calls.append(("enable_for_username", {"username": username}))

    def disable_for_username(self, username: str):
        self.calls.append(("disable_for_username", {"username": username}))

    def set_number_of_messages_per_completion(self, value: int):
        self.calls.append(("set_number_of_messages_per_completion", {"value": value}))
