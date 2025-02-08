from typing import Any, Dict, List
import aiohttp

from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import ChatformMessage
from app.src.gpt.gpt_completer import GptCompleter
from app.src.gpt.gpt_conf import GptConf
from app.src.observability.logger import Logger

logger = Logger(__name__)


# TODO: consider adding tenacity to retry requests in case of failure.
class OpenaiGptCompleter(GptCompleter):
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
            "messages": chatform.messages(),
        }
        if cfg.model() == "o3-mini":
            del kwargs["temperature"]
            del kwargs["max_tokens"]
            kwargs["max_completion_tokens"] = cfg.max_tokens()
        if len(functions) > 0:
            kwargs["functions"] = functions
            kwargs["function_call"] = "auto"
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                cfg.url(),
                json=kwargs,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {cfg.token()}",
                },
            ) as response:
                if response.status >= 400:
                    text = await response.text()
                    logger.error("Failed to complete:\n%s", text)
                response.raise_for_status()
                data = await response.json()
                return ChatformMessage.from_result_object(data)
