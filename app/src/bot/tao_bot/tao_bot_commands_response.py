from typing import Any, Callable, Coroutine, Optional
from app.src.butter.checks import check_optional


REPLY_ACTION_TYPE = Callable[[], Coroutine[Any, Any, str]]


class TaoBotCommandsResponse:
    class Builder:
        def __init__(self):
            self._ignore: bool = False
            self._reply_action: Optional[REPLY_ACTION_TYPE] = None

        def reply_action(
            self, coroutine: Optional[REPLY_ACTION_TYPE]
        ) -> "TaoBotCommandsResponse.Builder":
            self._reply_action = coroutine
            return self

        def build(self):
            return TaoBotCommandsResponse(self)

    def __init__(self, builder: Builder):
        self.reply_action: Optional[REPLY_ACTION_TYPE] = check_optional(
            builder._reply_action, "reply_action", Callable  # type: ignore
        )


def ignore():
    return TaoBotCommandsResponse.Builder().build()


def reply(post: str):
    async def wrapper() -> str:
        return post

    return TaoBotCommandsResponse.Builder().reply_action(wrapper).build()
