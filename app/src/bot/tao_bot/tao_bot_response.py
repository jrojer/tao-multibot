from typing import Optional, Callable
from app.src.butter.checks import check_type


class TaoBotResponse:
    class Builder:
        def __init__(self):
            self._ignore: bool = False
            self._reply_action: Callable = None
            self._postreply_action: Callable = None

        def reply_action(self, coroutine: Callable) -> "TaoBotResponse.Builder":
            self._reply_action = coroutine
            return self

        def postreply_action(self, coroutine: Callable) -> "TaoBotResponse.Builder":
            self._postreply_action = coroutine
            return self

        def build(self):
            return TaoBotResponse(self)

    def __init__(self, builder: Builder):
        self.reply_action: Optional[Callable] = check_type(
            builder._reply_action, "reply_action", Callable
        )
        self.postreply_action: Optional[Callable] = check_type(
            builder._postreply_action, "postreply_action", Callable
        )

    def no_reply(self):
        return self.reply_action is None

    def has_postreply(self):
        return self.postreply_action is not None


def ignore():
    return TaoBotResponse.Builder().build()


def reply_text(post: str):
    async def wrapper():
        return post

    return TaoBotResponse.Builder().reply_action(wrapper).build()


def reply(reply_action: Callable, postreply_action: Callable) -> TaoBotResponse:
    return (
        TaoBotResponse.Builder()
        .reply_action(reply_action)
        .postreply_action(postreply_action)
        .build()
    )
