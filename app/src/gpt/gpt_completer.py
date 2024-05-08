from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import ChatformMessage


class GptCompleter(ABC):
    @abstractmethod
    async def complete(
        self,
        chatform: Chatform,
        functions: List[Dict[str, Any]] = [],
        force_json: bool = False,
    ) -> ChatformMessage:
        pass
