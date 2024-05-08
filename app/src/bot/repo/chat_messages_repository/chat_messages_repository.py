from abc import ABC, abstractmethod
from typing import List

from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage


class ChatMessagesRepository(ABC):
    @abstractmethod
    def update_by_id(self, message: ChatMessage, id: str) -> None:
        pass

    @abstractmethod
    def add(self, message: ChatMessage) -> str:
        pass

    @abstractmethod
    def delete_by_chat_id(self, chat_id: str) -> None:
        pass

    @abstractmethod
    def fetch_last_messages_by_chat_id(
        self, chat_id: str, limit: int = 1000
    ) -> List[ChatMessage]:
        pass