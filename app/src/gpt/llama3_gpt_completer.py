from typing import Any, Dict, List
import aiohttp

from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import ChatformMessage
from app.src.gpt.gpt_completer import GptCompleter
from app.src.gpt.gpt_conf import GptConf
from app.src.observability.logger import Logger

logger = Logger(__name__)


class Llama3GptCompleter(GptCompleter):
    def __init__(self, config: GptConf):
        self._config = config

    async def complete(
        self,
        chatform: Chatform,
        functions: List[Dict[str, Any]] = [],
        force_json: bool = False,
    ) -> ChatformMessage:
        cfg = self._config
        kwargs: dict[str, Any] = {
            "model": cfg.model(),
            "temperature": cfg.temperature(),
            "max_tokens": cfg.max_tokens(),
            "top_p": cfg.top_p(),
            "presence_penalty": cfg.presence_penalty(),
            "frequency_penalty": cfg.frequency_penalty(),
            "messages": _reformated(chatform.messages()),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                cfg.url(),
                json=kwargs,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {cfg.token()}",
                },
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return ChatformMessage.from_result_object(data)


def _reformated(messages: list[ChatformMessage]) -> list[dict[str, Any]]:
    return [
        {
            "role": m.role(),
            "content": m.content(),
            "name": m.name(),
        }
        for m in messages
    ]
