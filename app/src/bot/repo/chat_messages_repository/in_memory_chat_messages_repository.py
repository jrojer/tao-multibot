from typing import List
from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import ChatMessagesRepository


class InMemoryMessagesRepository(ChatMessagesRepository):
    def __init__(self):
        self._messages: dict[str, ChatMessage] = {}

    def update_by_id(self, message: ChatMessage, id: str) -> None:
        self._messages[id] = message

    def add(self, message: ChatMessage) -> str:
        id = message.id()
        self._messages[id] = message
        return id

    def delete_by_chat_id(self, chat_id: str) -> None:
        self._messages = {
            id: m 
            for id, m in self._messages.items() 
            if m.chat_id() != chat_id
        }

    def fetch_last_messages_by_chat_id(
        self, chat_id: str, limit: int = 1000
    ) -> List[ChatMessage]:
        return [
            m 
            for m in self._messages.values() 
            if m.chat_id() == chat_id
        ][-limit:]
