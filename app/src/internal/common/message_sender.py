from abc import ABC, abstractmethod
from typing import Optional


class MessageSender(ABC):
    @abstractmethod
    async def send_text(
        self, chat_id: str, message: str, username: Optional[str]
    ) -> None:
        pass
