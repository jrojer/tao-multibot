from typing import Any, Callable, Coroutine, Optional
from app.src.butter.checks import check_type
from app.src.gpt.chatform_message import ChatformMessage


POSTREPLY_ACTION_TYPE = Callable[[], Coroutine[Any, Any, None]]
REPLY_ACTION_TYPE = Callable[[], Coroutine[Any, Any, ChatformMessage]]


class TaoBotResponse:
    class Builder:
        def __init__(self):
            self._ignore: bool = False
            self._reply_action: Optional[REPLY_ACTION_TYPE] = None
            self._postreply_action: Optional[POSTREPLY_ACTION_TYPE] = None

        def reply_action(
            self, coroutine: Optional[REPLY_ACTION_TYPE]
        ) -> "TaoBotResponse.Builder":
            self._reply_action = coroutine
            return self

        def postreply_action(
            self, coroutine: Optional[POSTREPLY_ACTION_TYPE]
        ) -> "TaoBotResponse.Builder":
            self._postreply_action = coroutine
            return self

        def build(self):
            return TaoBotResponse(self)

    def __init__(self, builder: Builder):
        self.reply_action: Optional[REPLY_ACTION_TYPE] = check_type(
            builder._reply_action, "reply_action", Callable  # type: ignore
        )
        self.postreply_action: Optional[POSTREPLY_ACTION_TYPE] = check_type(
            builder._postreply_action, "postreply_action", Callable  # type: ignore
        )

    def has_reply(self):
        return self.reply_action is not None

    def has_postreply(self):
        return self.postreply_action is not None


def ignore():
    return TaoBotResponse.Builder().build()


def reply(
    reply_action: Optional[REPLY_ACTION_TYPE],
    postreply_action: Optional[POSTREPLY_ACTION_TYPE],
) -> TaoBotResponse:
    return (
        TaoBotResponse.Builder()
        .reply_action(reply_action)
        .postreply_action(postreply_action)
        .build()
    )
