from typing import Any, List, Optional
from app.src.butter.checks import check_required
from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import ChatformMessage, function_result_message
from app.src.gpt.gpt_completer import GptCompleter
from app.src.gpt.plugin import Plugin
from app.src.observability.logger import Logger


logger = Logger(__name__)


class GptGateway:
    MAX_NUM_OF_FUNCTION_CALLS = 20

    def __init__(self, gpt_completer: GptCompleter):
        self._gpt_completer = check_required(
            gpt_completer, "gpt_completer", GptCompleter
        )

    async def forward(
        self,
        chatform: Chatform,
        plugins: List[Plugin] = [],
    ) -> ChatformMessage:
        manifests: list[dict[str, Any]] = [
            function["manifest"] for p in plugins for function in p.functions()
        ]
        plugin_by_function_name = {
            function["manifest"]["name"]: p
            for p in plugins
            for function in p.functions()
        }

        response_message: ChatformMessage = await self._gpt_completer.complete(
            chatform, manifests
        )

        function_call: Optional[ChatformMessage.FunctionCall] = (
            response_message.function_call()
        )

        num_of_function_calls = 0
        while function_call is not None:
            chatform.add_message(response_message)
            logger.info("Calling function: %s", function_call.name())

            plugin: Plugin = plugin_by_function_name[function_call.name()]

            result: str = await plugin.call(function_call.name(), function_call.arguments())

            result_message: ChatformMessage = function_result_message(function_call.name(), result)

            if plugin.is_delegate():
                return result_message

            chatform.add_message(result_message)

            response_message = await self._gpt_completer.complete(chatform, manifests)

            function_call = response_message.function_call()
            num_of_function_calls += 1
            if num_of_function_calls >= GptGateway.MAX_NUM_OF_FUNCTION_CALLS:
                raise RuntimeError("Max number of function calls exceeded.")

        return response_message
