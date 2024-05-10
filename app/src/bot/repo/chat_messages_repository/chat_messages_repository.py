from abc import ABC, abstractmethod
from typing import List

from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage


class ChatMessagesRepository(ABC):
    @abstractmethod
    def add(self, message: ChatMessage) -> str:
        pass

    @abstractmethod
    def fetch_last_messages_by_chat_id(
        self, chat: str, limit: int = 1000
    ) -> List[ChatMessage]:
        pass
