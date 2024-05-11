from abc import ABC, abstractmethod
from typing import Any

class ConfClient(ABC):
    @abstractmethod
    def get_bot_conf(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def enable_for_group(self, chat_id: str):
        pass

    @abstractmethod
    def disable_for_group(self, chat_id: str):
        pass

    @abstractmethod
    def enable_for_username(self, username: str):
        pass

    @abstractmethod
    def disable_for_username(self, username: str):
        pass

    @abstractmethod
    def set_number_of_messages_per_completion(self, value: int):
        pass
