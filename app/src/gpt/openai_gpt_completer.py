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
    async def complete(
        self,
        config: GptConf,
        chatform: Chatform,
        functions: List[Dict[str, Any]] = [],
        force_json=False,
    ) -> ChatformMessage:
        kwargs = {
            "model": config.model(),
            "temperature": config.temperature(),
            "max_tokens": config.max_tokens(),
            "top_p": config.top_p(),
            "presence_penalty": config.presence_penalty(),
            "frequency_penalty": config.frequency_penalty(),
            "messages": chatform.messages(),
        }
        if len(functions) > 0:
            kwargs["functions"] = functions
            kwargs["function_call"] = "auto"
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json=kwargs,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.token()}",
                },
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return ChatformMessage.from_result_object(data)
