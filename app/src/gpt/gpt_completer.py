from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import ChatformMessage
from app.src.gpt.gpt_conf import GptConf


# TODO: consider adding tenacity to retry requests in case of failure.
class GptCompleter(ABC):
    @abstractmethod
    async def complete(
        self,
        chatform: Chatform,
        functions: List[Dict[str, Any]] = [],
        force_json=False,
    ) -> ChatformMessage:
        pass
