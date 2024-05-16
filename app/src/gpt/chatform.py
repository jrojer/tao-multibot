from typing import Any, List
from app.src.butter.checks import check_required
from app.src.gpt.chatform_message import ChatformMessage, system_message
from app.src.observability.logger import Logger


logger = Logger(__name__)


MESSAGES = "messages"
SYSTEM_PROMPT = "system_prompt"


# TODO: add strategies to handle scenarios when we need to restrict chatform's token length.
# Possible strategies:
# - add token length limit and remove oldest messages until the limit is satisfied.
#   That has corner cases when a single message is longer than the limit.
# - truncate all messages to the limit.
class Chatform:
    def __init__(
        self,
        system_prompt: str,
    ):
        self._messages: List[ChatformMessage] = []
        self._system_prompt: ChatformMessage = system_message(system_prompt)

    def add_message(self, chatform_message: ChatformMessage):
        self._messages.append(chatform_message)
        return self

    def copy(self):
        chatform = Chatform(check_required(self._system_prompt.content(), "system_prompt", str))
        chatform._messages = self._messages.copy()
        return chatform

    def clear(self):
        self._messages = []

    def messages(self) -> list[dict[str, Any]]:
        result = [self._system_prompt.to_dict()]
        for message in self._messages:
            result.append(message.to_dict())
        return result

    def to_dict(self):
        return {
            SYSTEM_PROMPT: self._system_prompt.to_dict(),
            MESSAGES: [m.to_dict() for m in self._messages],
        }
