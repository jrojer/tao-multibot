from typing import List
from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import ChatMessagesRepository


class InMemoryChatMessagesRepository(ChatMessagesRepository):
    def __init__(self):
        self._messages: dict[str, ChatMessage] = {}

    def add(self, message: ChatMessage) -> str:
        id = message.id()
        self._messages[id] = message
        return id

    def fetch_last_messages_by_chat_and_adder(
        self, chat: str, adder: str, limit: int = 1000
    ) -> List[ChatMessage]:
        return [
            m 
            for m in self._messages.values() 
            if m.chat() == chat and m.added_by() == adder
        ][-limit:]
